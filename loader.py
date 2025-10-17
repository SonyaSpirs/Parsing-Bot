import logging
from telegram.ext import Application
from data.config import BotConfig
from bot.handlers.user_handlers import UserHandlers
from bot.handlers.callback_handlers import CallbackHandlers

logger = logging.getLogger(__name__)

class BotLoader:
    def __init__(self):
        self.config = BotConfig()
        self.application = None
        self.user_articles = {}  # Менеджер состояния пользователей

    def setup_handlers(self):
        """Настройка всех обработчиков"""
        # Инициализация обработчиков
        user_handlers = UserHandlers(self.user_articles)
        callback_handlers = CallbackHandlers(self.user_articles)

        # Добавление обработчиков
        for handler in user_handlers.get_handlers():
            self.application.add_handler(handler)

        for handler in callback_handlers.get_handlers():
            self.application.add_handler(handler)

    def setup_error_handler(self):
        """Настройка обработчика ошибок"""
        async def error_handler(update, context):
            logger.error(f"Exception while handling an update: {context.error}")
            try:
                if update and update.effective_chat:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ Произошла ошибка. Пожалуйста, попробуйте еще раз."
                    )
            except Exception as e:
                logger.error(f"Error in error handler: {e}")

        self.application.add_error_handler(error_handler)

    def load_bot(self):
        """Загрузка и настройка бота"""
        self.application = Application.builder().token(self.config.TOKEN).build()
        
        self.setup_handlers()
        self.setup_error_handler()
        
        return self.application
