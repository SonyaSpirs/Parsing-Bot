import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from parser import ITProgerParser
import html

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class ITProgerBot:
    def __init__(self):
        self.parser = ITProgerParser()
        self.user_data = {}  # Храним данные пользователей

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        welcome_text = f"""
👋 Привет, {user.first_name}!

🤖 Я бот для чтения IT статей с itproger.com/news

📚 Доступные команды:
/news - Последние статьи
/next - Следующая страница
/prev - Предыдущая страница

🎛️ Используй кнопки ниже для навигации!
        """

        # Reply клавиатура
        reply_keyboard = [
            ["📰 Последние новости"],
            ["➡️ Следующая страница", "⬅️ Предыдущая страница"],
            ["ℹ️ Помощь"]
        ]

        await update.message.reply_text(
            welcome_text,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
                input_field_placeholder="Выберите действие..."
            )
        )

    async def show_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает последние новости"""
        user_id = update.effective_user.id

        # Инициализируем данные пользователя
        if user_id not in self.user_data:
            self.user_data[user_id] = {'current_page': 1}

        await self._send_articles(update, context, page=1)

    async def next_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Следующая страница"""
        user_id = update.effective_user.id

        if user_id not in self.user_data:
            self.user_data[user_id] = {'current_page': 1}

        current_page = self.user_data[user_id]['current_page']
        next_page = current_page + 1

        await self._send_articles(update, context, page=next_page)

    async def prev_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Предыдущая страница"""
        user_id = update.effective_user.id

        if user_id not in self.user_data:
            self.user_data[user_id] = {'current_page': 1}

        current_page = self.user_data[user_id]['current_page']
        prev_page = max(1, current_page - 1)

        await self._send_articles(update, context, page=prev_page)

    async def _send_articles(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
        """Отправляет статьи указанной страницы"""
        user_id = update.effective_user.id

        # Сохраняем текущую страницу
        self.user_data[user_id]['current_page'] = page

        # Получаем статьи
        articles = self.parser.get_articles(page)

        if not articles:
            await update.message.reply_text(
                "❌ Не удалось загрузить статьи. Попробуйте позже."
            )
            return

        # Инлайн клавиатура для навигации
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_{page}"))
        nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"next_{page}"))

        navigation = [nav_buttons] if nav_buttons else []

        # Отправляем каждую статью отдельным сообщением
        for i, article in enumerate(articles, 1):
            message_text = self._format_article_message(article, i, page)

            # Кнопки для статьи
            article_buttons = [
                [
                    InlineKeyboardButton("📖 Полный текст", callback_data=f"full_{article['link']}"),
                    InlineKeyboardButton("🔗 Открыть статью", url=article['link'])
                ]
            ]

            # Добавляем навигацию к последней статье
            if i == len(articles):
                article_buttons.extend(navigation)

            reply_markup = InlineKeyboardMarkup(article_buttons)

            try:
                if article['image_url']:
                    await update.message.reply_photo(
                        photo=article['image_url'],
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text(
                        message_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
            except Exception as e:
                # Если не удалось отправить с фото, отправляем только текст
                await update.message.reply_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

    def _format_article_message(self, article, index, page):
        """Форматирует сообщение со статьей"""
        title = html.escape(article['title'])
        description = html.escape(article['description'])

        return f"""
📰 <b>{title}</b>

📝 {description}

📄 Страница: {page} | Статья: {index}
        """

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на инлайн кнопки"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith('full_'):
            # Кнопка "Полный текст"
            article_url = data[5:]
            full_content = self.parser.get_full_content(article_url)

            if full_content:
                # Экранируем HTML символы для Markdown
                content = html.escape(full_content)
                message = f"📖 <b>Полное содержимое:</b>\n\n{content}"
            else:
                message = "⏳ <b>Скоро!</b>\n\nПолное содержимое статьи будет доступно в ближайшее время."

            await query.edit_message_caption(
                caption=query.message.caption + f"\n\n{message}" if query.message.caption else message,
                parse_mode='HTML'
            )

        elif data.startswith('next_'):
            # Следующая страница
            current_page = int(data[5:])
            user_id = query.from_user.id
            self.user_data[user_id] = {'current_page': current_page + 1}

            articles = self.parser.get_articles(current_page + 1)
            if articles:
                await self._edit_message_with_articles(query, articles, current_page + 1)
            else:
                await query.edit_message_caption(
                    caption="❌ Больше статей нет",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_{current_page}")]
                    ])
                )

        elif data.startswith('prev_'):
            # Предыдущая страница
            current_page = int(data[5:])
            prev_page = max(1, current_page - 1)
            user_id = query.from_user.id
            self.user_data[user_id] = {'current_page': prev_page}

            articles = self.parser.get_articles(prev_page)
            await self._edit_message_with_articles(query, articles, prev_page)

    async def _edit_message_with_articles(self, query, articles, page):
        """Редактирует сообщение с новыми статьями"""
        if not articles:
            await query.edit_message_caption(
                caption="❌ Не удалось загрузить статьи",
                reply_markup=None
            )
            return

        # Берем первую статью для отображения
        article = articles[0]
        message_text = self._format_article_message(article, 1, page)

        # Кнопки для навигации
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_{page}"))
        nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"next_{page}"))

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📖 Полный текст", callback_data=f"full_{article['link']}"),
                InlineKeyboardButton("🔗 Открыть статью", url=article['link'])
            ],
            nav_buttons
        ])

        try:
            if query.message.photo:
                await query.edit_message_caption(
                    caption=message_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
        except Exception as e:
            logging.error(f"Ошибка редактирования сообщения: {e}")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text

        if text == "📰 Последние новости":
            await self.show_news(update, context)
        elif text == "➡️ Следующая страница":
            await self.next_page(update, context)
        elif text == "⬅️ Предыдущая страница":
            await self.prev_page(update, context)
        elif text == "ℹ️ Помощь":
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "🤔 Не понимаю команду. Используйте кнопки или команды из меню."
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает справку"""
        help_text = """
📚 <b>Доступные команды:</b>

<b>Команды:</b>
/start - Начать работу
/news - Последние статьи
/next - Следующая страница  
/prev - Предыдущая страница
/help - Эта справка

<b>Кнопки:</b>
📖 Полный текст - Показать полное содержимое статьи
🔗 Открыть статью - Открыть оригинал на itproger.com
⬅️/➡️ - Навигация по страницам

<b>Поддержка Markdown:</b>
Бот поддерживает форматирование кода через Markdown
        """
        await update.message.reply_text(help_text, parse_mode='HTML')


def main():
    """Запуск бота"""
    bot = ITProgerBot()

    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("news", bot.show_news))
    application.add_handler(CommandHandler("next", bot.next_page))
    application.add_handler(CommandHandler("prev", bot.prev_page))
    application.add_handler(CommandHandler("help", bot.help_command))

    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text))

    # Запускаем бота
    print("🤖 Бот запущен!")
    application.run_polling()


if __name__ == '__main__':
    main()