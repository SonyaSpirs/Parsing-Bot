from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class InlineKeyboards:
    def __init__(self, user_articles_manager):
        self.user_articles = user_articles_manager

    def create_article_preview_keyboard(self, article_index: int, user_id: int) -> InlineKeyboardMarkup:
        """Создание клавиатуры для превью статьи"""
        if user_id in self.user_articles and article_index < len(self.user_articles[user_id]):
            article_link = self.user_articles[user_id][article_index]['link']
        else:
            article_link = "https://itproger.com/news"

        keyboard = [
            [
                InlineKeyboardButton("📖 Читать в боте", callback_data=f"brief_{article_index}"),
                InlineKeyboardButton("🌐 На сайт", url=article_link)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def create_article_content_keyboard(self, article_index: int, user_id: int) -> InlineKeyboardMarkup:
        """Создание клавиатуры для содержимого статьи"""
        if user_id in self.user_articles and article_index < len(self.user_articles[user_id]):
            article_link = self.user_articles[user_id][article_index]['link']
        else:
            article_link = "https://itproger.com/news"

        keyboard = [
            [
                InlineKeyboardButton("🌐 Читать на сайте", url=article_link),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_list")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def create_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Создает главное меню"""
        keyboard = [
            [InlineKeyboardButton("📰 Последние новости", callback_data="menu_news")],
            [InlineKeyboardButton("🧪 Тестовые новости", callback_data="menu_test")],
            [InlineKeyboardButton("🆘 Помощь", callback_data="menu_help")],
            [InlineKeyboardButton("ℹ️ О боте", callback_data="menu_about")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def create_news_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Создает меню для раздела новостей"""
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить новости", callback_data="menu_news")],
            [InlineKeyboardButton("🧪 Тестовые новости", callback_data="menu_test")],
            [InlineKeyboardButton("📋 Главное меню", callback_data="menu_main")],
            [InlineKeyboardButton("🆘 Помощь", callback_data="menu_help")]
        ]
        return InlineKeyboardMarkup(keyboard)
