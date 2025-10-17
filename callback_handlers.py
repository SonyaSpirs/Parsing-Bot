import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.keyboards.inline import InlineKeyboards
from bot.parser.itproger_parser import ITProgerParser
import asyncio

logger = logging.getLogger(__name__)

class CallbackHandlers:
    def __init__(self, user_articles_manager):
        self.user_articles = user_articles_manager
        self.parser = ITProgerParser()
        self.inline_keyboards = InlineKeyboards(user_articles_manager)

    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        try:
            if data.startswith("brief_"):
                article_index = int(data.split("_")[1])
                await self.show_article_content(query, context, article_index, user_id)

            elif data == "back_to_list":
                await query.edit_message_text(
                    "↩️ Используйте /news для нового списка статей!",
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error in handle_button: {e}")
            await query.edit_message_text("❌ Ошибка. Попробуйте снова.")

    async def show_article_content(self, query, context: ContextTypes.DEFAULT_TYPE, article_index: int, user_id: int):
        """Показать содержимое статьи"""
        try:
            if user_id not in self.user_articles or article_index >= len(self.user_articles[user_id]):
                await query.edit_message_text("❌ Статья не найдена. Используйте /news")
                return

            article = self.user_articles[user_id][article_index]

            await query.edit_message_text(f"📖 Загружаю: {article['title']}...")

            full_content = self.parser.get_article_full_content(article['link'])
            message_text = f"**{article['title']}**\n\n{full_content}"

            keyboard = self.inline_keyboards.create_article_content_keyboard(article_index, user_id)

            # Проверяем длину сообщения
            if len(message_text) > 4096:
                part1 = message_text[:4000]
                part2 = message_text[4000:]

                await query.edit_message_text(part1, parse_mode='Markdown')
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=part2,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error showing article: {e}")
            await query.edit_message_text(
                text=f"❌ Не удалось загрузить статью.\n\n📖 Читайте на сайте: {article['link']}",
                parse_mode='Markdown'
            )

    def get_handlers(self):
        """Возвращает список обработчиков callback'ов"""
        return [
            CallbackQueryHandler(self.handle_button, pattern="^(brief_|back_|site_)")
        ]
