# import json
# import requests
# import re
# import urllib.parse
# import html
# import time
# from bs4 import BeautifulSoup
#
#
# class TelegramBot:
#     def __init__(self, token):
#         self.token = token
#         self.base_url = f"https://api.telegram.org/bot{token}/"
#
#     def get_updates(self, offset=None):
#         url = self.base_url + "getUpdates"
#         params = {
#             "timeout": 30,
#             "offset": offset
#         }
#         result = self._make_request(url, params, method="GET")
#         return json.loads(result) if result else None
#
#     def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML"):
#         url = self.base_url + "sendMessage"
#         data = {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": parse_mode
#         }
#         if reply_markup:
#             data["reply_markup"] = json.dumps(reply_markup)
#         return self._make_request(url, data)
#
#     def send_photo(self, chat_id, photo_url, caption="", reply_markup=None):
#         url = self.base_url + "sendPhoto"
#         data = {
#             "chat_id": chat_id,
#             "photo": photo_url,
#             "caption": caption,
#             "parse_mode": "HTML"
#         }
#         if reply_markup:
#             data["reply_markup"] = json.dumps(reply_markup)
#         return self._make_request(url, data)
#
#     def edit_message_reply_markup(self, chat_id, message_id, reply_markup=None):
#         url = self.base_url + "editMessageReplyMarkup"
#         data = {
#             "chat_id": chat_id,
#             "message_id": message_id
#         }
#         if reply_markup:
#             data["reply_markup"] = json.dumps(reply_markup)
#         return self._make_request(url, data)
#
#     def answer_callback_query(self, callback_query_id, text=None):
#         url = self.base_url + "answerCallbackQuery"
#         data = {
#             "callback_query_id": callback_query_id
#         }
#         if text:
#             data["text"] = text
#         return self._make_request(url, data)
#
#     @staticmethod
#     def _make_request(url, data=None, method="POST"):
#         try:
#             if method == "GET":
#                 response = requests.get(url, params=data, timeout=30)
#             else:
#                 response = requests.post(url, data=data, timeout=30)
#             return response.text
#         except Exception as e:
#             print(f"Request error: {e}")
#             return None
#
#
# class ItProgerParser:
#     def __init__(self):
#         self.base_url = "https://itproger.com/news"
#         self.session = requests.Session()
#         self.session.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#             'Referer': 'https://itproger.com/',
#         })
#
#     def get_news_page(self, page=1):
#         """Get news page from itproger.com"""
#         try:
#             if page > 1:
#                 url = f"{self.base_url}/{page}"
#             else:
#                 url = self.base_url
#
#             print(f"Loading: {url}")
#             response = self.session.get(url, timeout=15)
#             response.raise_for_status()
#
#             # Сохраняем HTML для отладки
#             with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
#                 f.write(response.text)
#             print(f"✅ Page saved to debug_page_{page}.html")
#
#             return response.text
#         except Exception as e:
#             print(f"❌ Page loading error: {e}")
#             return None
#
#     def parse_news_cards(self, html_content):
#         """Parse news cards from ItProger with multiple methods"""
#         if not html_content:
#             print("❌ No HTML content provided")
#             return []
#
#         soup = BeautifulSoup(html_content, 'html.parser')
#         articles = []
#
#         print("🔍 Starting parsing with multiple methods...")
#
#         # Метод 1: Ищем статьи по структуре ItProger
#         articles.extend(self._parse_by_articles(soup))
#
#         # Метод 2: Ищем по карточкам
#         articles.extend(self._parse_by_cards(soup))
#
#         # Метод 3: Ищем по grid-структуре
#         articles.extend(self._parse_by_grid(soup))
#
#         # Метод 4: Ищем все ссылки с новостями
#         articles.extend(self._parse_by_links(soup))
#
#         # Убираем дубликаты
#         unique_articles = []
#         seen_titles = set()
#         for article in articles:
#             if article['title'] and article['title'] not in seen_titles:
#                 unique_articles.append(article)
#                 seen_titles.add(article['title'])
#
#         print(f"✅ Total unique articles found: {len(unique_articles)}")
#
#         # Сохраняем результаты для отладки
#         with open("debug_articles.json", "w", encoding="utf-8") as f:
#             json.dump(unique_articles, f, ensure_ascii=False, indent=2)
#
#         return unique_articles
#
#     def _parse_by_articles(self, soup):
#         """Parse using article tags"""
#         articles = []
#         news_articles = soup.find_all('article')
#         print(f"🔍 Found {len(news_articles)} article tags")
#
#         for article in news_articles:
#             try:
#                 parsed = self._parse_article_element(article)
#                 if parsed and parsed['title']:
#                     articles.append(parsed)
#                     print(f"✅ Article: {parsed['title'][:50]}...")
#             except Exception as e:
#                 continue
#         return articles
#
#     def _parse_by_cards(self, soup):
#         """Parse using card-like divs"""
#         articles = []
#
#         # Ищем карточки с новостями
#         card_selectors = [
#             'div[class*="news"]',
#             'div[class*="article"]',
#             'div[class*="post"]',
#             'div[class*="card"]',
#             'div[class*="item"]',
#             'div[class*="blog"]',
#             'div[class*="content"]'
#         ]
#
#         for selector in card_selectors:
#             cards = soup.select(selector)
#             print(f"🔍 Selector '{selector}': found {len(cards)} elements")
#
#             for card in cards[:10]:  # Проверяем первые 10
#                 try:
#                     parsed = self._parse_article_element(card)
#                     if parsed and parsed['title'] and len(parsed['title']) > 10:
#                         articles.append(parsed)
#                         print(f"✅ Card: {parsed['title'][:50]}...")
#                 except Exception as e:
#                     continue
#
#         return articles
#
#     def _parse_by_grid(self, soup):
#         """Parse grid and flex containers"""
#         articles = []
#
#         # Ищем grid и flex контейнеры
#         grid_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(
#             word in str(x).lower() for word in ['grid', 'flex', 'row', 'container', 'wrapper']
#         ))
#
#         print(f"🔍 Found {len(grid_containers)} grid/flex containers")
#
#         for container in grid_containers:
#             # Ищем внутри контейнера элементы с контентом
#             content_elems = container.find_all(['div', 'article', 'section'])
#             for elem in content_elems:
#                 try:
#                     parsed = self._parse_article_element(elem)
#                     if parsed and parsed['title'] and len(parsed['title']) > 10:
#                         articles.append(parsed)
#                         print(f"✅ Grid item: {parsed['title'][:50]}...")
#                 except Exception as e:
#                     continue
#
#         return articles
#
#     def _parse_by_links(self, soup):
#         """Parse by finding news links"""
#         articles = []
# links
#         # Ищем все ссылки которые могут вести на новости
#         news_links = soup.find_all('a', href=re.compile(r'/news/|/article/|/post/'))
#         print(f"🔍 Found {len(news_links)} news-like links")
#
#         for link in news_links:
#             try:
#                 # Получаем родительский элемент для большего контекста
#                 parent = link.find_parent(['div', 'article', 'li'])
#                 context_elem = parent if parent else link
#
#                 article = {
#                     'title': self._clean_text(link.get_text()),
#                     'url': self._make_absolute_url(link.get('href')),
#                     'image': '',
#                     'excerpt': '',
#                     'tags': []
#                 }
#
#                 # Ищем изображение рядом
#                 img = context_elem.find('img')
#                 if img:
#                     article['image'] = self._make_absolute_url(img.get('src') or img.get('data-src'))
#
#                 # Ищем описание
#                 desc = context_elem.find('p') or context_elem.find('span')
#                 if desc:
#                     article['excerpt'] = self._clean_text(desc.get_text())[:150] + "..."
#
#                 if article['title'] and len(article['title']) > 10:
#                     articles.append(article)
#                     print(f"✅ Link: {article['title'][:50]}...")
#
#             except Exception as e:
#                 continue
#
#         return articles
#
#     def _parse_article_element(self, elem):
#         """Parse individual article element"""
#         article = {
#             'title': '',
#             'image': '',
#             'excerpt': '',
#             'url': '',
#             'tags': []
#         }
#
#         # Заголовок - ищем во всех возможных тегах
#         title_elem = (
#                 elem.find('h1') or elem.find('h2') or elem.find('h3') or
#                 elem.find('h4') or elem.find(['a', 'span'], class_=lambda x: x and any(
#             word in str(x).lower() for word in ['title', 'head', 'name']
#         ))
#         )
#
#         if title_elem:
#             article['title'] = self._clean_text(title_elem.get_text())
#
#         # Ссылка
#         link_elem = elem.find('a', href=True)
#         if link_elem:
#             href = link_elem.get('href')
#             if href and ('/news/' in href or '/article/' in href):
#                 article['url'] = self._make_absolute_url(href)
#
#         # Изображение
#         img_elem = elem.find('img')
#         if img_elem:
#             src = img_elem.get('src') or img_elem.get('data-src')
#             if src:
#                 article['image'] = self._make_absolute_url(src)
#
#         # Описание
#         desc_elem = elem.find('p') or elem.find('div', class_=lambda x: x and any(
#             word in str(x).lower() for word in ['desc', 'text', 'content', 'excerpt', 'preview']
#         ))
#         if desc_elem:
#             text = self._clean_text(desc_elem.get_text())
#             if len(text) > 20:
#                 article['excerpt'] = text[:200] + "..." if len(text) > 200 else text
#
#         # Если нет описания, создаем стандартное
#         if not article['excerpt'] and article['title']:
#             article['excerpt'] = "IT-новость с ItProger. Нажмите для чтения полной версии."
#
#         return article
#
#     def get_full_article(self, article_url):
#         """Get full article content"""
#         try:
#             print(f"📖 Loading full article: {article_url}")
#             response = self.session.get(article_url, timeout=10)
#             response.raise_for_status()
#
#             soup = BeautifulSoup(response.text, 'html.parser')
#
#             # Заголовок
#             title = soup.find('h1')
#             title_text = self._clean_text(title.get_text()) if title else ""
#
#             # Основной контент
#             content_selectors = [
#                 'article',
#                 '.article-content',
#                 '.post-content',
#                 '.content',
#                 'main',
#                 '.news-content',
#                 '.entry-content'
#             ]
#
#             content_elem = None
#             for selector in content_selectors:
#                 content_elem = soup.select_one(selector)
#                 if content_elem:
#                     break
#
#             if not content_elem:
#                 content_elem = soup.find('body')
#
#             content_text = ""
#             if content_elem:
#                 # Удаляем ненужные элементы
#                 for unwanted in content_elem.find_all(['script', 'style', 'nav', 'aside', 'header', 'footer']):
#                     unwanted.decompose()
#
#                 # Собираем текст
#                 paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'li'])
#                 text_parts = []
#
#                 for p in paragraphs:
#                     text = self._clean_text(p.get_text())
#                     if len(text) > 20:
#                         if p.name in ['h2', 'h3']:
#                             text_parts.append(f"\n🔹 {text}\n")
#                         elif p.name == 'li':
#                             text_parts.append(f"• {text}")
#                         else:
#                             text_parts.append(text)
#
#                 content_text = '\n'.join(text_parts)
#
#             result = f"<b>{title_text}</b>\n\n{content_text}" if title_text else content_text
#             return result[:3800] + "..." if len(result) > 3800 else result
#
#         except Exception as e:
#             print(f"❌ Error loading full article: {e}")
#             return "Не удалось загрузить полный текст статьи. Посетите сайт для чтения."
#
#     @staticmethod
#     def _make_absolute_url(url):
#         """Convert relative URL to absolute"""
#         if not url:
#             return ""
#         if url.startswith('//'):
#             return 'https:' + url
#         elif url.startswith('/'):
#             return 'https://itproger.com' + url
#         elif not url.startswith('http'):
#             return 'https://itproger.com/' + url
#         return url
#
#     @staticmethod
#     def _clean_text(text):
#         """Clean text from extra spaces"""
#         if not text:
#             return ""
#         text = html.unescape(text)
#         text = re.sub(r'\s+', ' ', text)
#         text = re.sub(r'\n+', '\n', text)
#         text = text.strip()
#         return text
#
#
# def get_main_menu_keyboard():
#     """Main menu keyboard"""
#     return {
#         "keyboard": [
#             [{"text": "📰 Все новости"}],
#             [{"text": "🔄 Обновить"}, {"text": "🆘 Помощь"}]
#         ],
#         "resize_keyboard": True,
#         "one_time_keyboard": False
#     }
#
#
# def get_news_navigation_keyboard(page, has_next=True):
#     """News navigation inline keyboard"""
#     buttons = []
#
#     if page > 1:
#         buttons.append({"text": "◀️ Назад", "callback_data": f"news_page_{page - 1}"})
#
#     buttons.append({"text": f"📄 {page}", "callback_data": "current_page"})
#
#     if has_next:
#         buttons.append({"text": "Вперед ▶️", "callback_data": f"news_page_{page + 1}"})
#
#     return {"inline_keyboard": [buttons]}
#
#
# def get_article_keyboard(article_url, page, article_index, total_articles):
#     """Article inline keyboard"""
#     return {
#         "inline_keyboard": [
#             [
#                 {"text": "📖 Читать полностью", "callback_data": f"full_article_{article_url}"},
#                 {"text": "🌐 На сайт", "url": article_url}
#             ],
#             [
#                 {"text": "⬅️ Предыдущая",
#                  "callback_data": f"article_{page}_{article_index - 1}"} if article_index > 0 else {"text": "⏹️",
#                                                                                                     "callback_data": "none"},
#                 {"text": f"{article_index + 1}/{total_articles}", "callback_data": "current_article"},
#                 {"text": "Следующая ➡️",
#                  "callback_data": f"article_{page}_{article_index + 1}"} if article_index < total_articles - 1 else {
#                     "text": "⏹️", "callback_data": "none"}
#             ],
#             [
#                 {"text": "🔙 К списку страниц", "callback_data": f"news_page_{page}"}
#             ]
#         ]
#     }
#
#
# def format_article_card(article, index, total):
#     """Format article card for sending"""
#     caption = f"<b>📰 {article['title']}</b>\n\n"
#
#     if article['excerpt']:
#         caption += f"{article['excerpt']}\n\n"
#
#     caption += f"📊 Новость {index + 1} из {total}"
#     return caption
#
#
# def handle_message(bot, parser, message):
#     chat_id = message['chat']['id']
#     text = message.get('text', '')
#
#     if text in ['/start', '🚀 Старт']:
#         welcome_text = (
#             "👋 <b>Добро пожаловать в IT News Parser Bot!</b>\n\n"
#             "📰 <b>Получайте все IT-новости с ItProger</b>\n\n"
#             "🔹 <b>Функции:</b>\n"
#             "• Все новости с itproger.com/news\n"
#             "• Просмотр всех тегов и содержимого\n"
#             "• Навигация между новостями\n"
#             "• Прямые ссылки на сайт\n"
#             "• Полные тексты статей\n\n"
#             "🚀 <b>Нажмите 'Все новости' чтобы увидеть все статьи!</b>"
#         )
#         bot.send_message(chat_id, welcome_text, get_main_menu_keyboard())
#
#     elif text in ['📰 Все новости', '🔄 Обновить']:
#         bot.send_message(chat_id, "⏳ Загружаю все IT-новости с ItProger...")
#         show_news_page(bot, parser, chat_id, 1)
#
#     elif text in ['🆘 Помощь', '/help']:
#         help_text = (
#             "📖 <b>Помощь по IT News Parser Bot</b>\n\n"
#             "🤖 <b>Как использовать:</b>\n"
#             "1. Нажмите <b>Все новости</b>\n"
#             "2. Просматривайте все найденные статьи\n"
#             "3. Используйте кнопки навигации между новостями\n"
#             "4. Нажмите <b>Читать полностью</b> для полного текста\n"
#             "5. Нажмите <b>На сайт</b> для открытия на ItProger\n\n"
#             "🔄 <b>Обновить</b> - перезагрузить новости\n\n"
#             "💡 <b>Источник:</b> itproger.com/news"
#         )
#         bot.send_message(chat_id, help_text, get_main_menu_keyboard())
#
#     else:
#         unknown_text = (
#             "❌ <b>Неизвестная команда</b>\n\n"
#             "Используйте кнопки меню для навигации.\n\n"
#             "Для справки нажмите <b>🆘 Помощь</b>"
#         )
#         bot.send_message(chat_id, unknown_text, get_main_menu_keyboard())
#
#
# def handle_callback(bot, parser, callback_query):
#     chat_id = callback_query['message']['chat']['id']
#     message_id = callback_query['message']['message_id']
#     callback_data = callback_query['data']
#     callback_id = callback_query['id']
#
#     if callback_data.startswith('news_page_'):
#         page = int(callback_data.split('_')[-1])
#         bot.answer_callback_query(callback_id, f"Загружаем страницу {page}...")
#         show_news_page(bot, parser, chat_id, page, message_id)
#
#     elif callback_data.startswith('article_'):
#         parts = callback_data.split('_')
#         page = int(parts[1])
#         article_index = int(parts[2])
#         bot.answer_callback_query(callback_id, f"Переходим к новости {article_index + 1}...")
#         show_specific_article(bot, parser, chat_id, page, article_index, message_id)
#
#     elif callback_data.startswith('full_article_'):
#         article_url = callback_data.replace('full_article_', '')
#         bot.answer_callback_query(callback_id, "Загружаем полный текст...")
#         show_full_article(bot, parser, chat_id, article_url)
#
#     elif callback_data in ['current_page', 'current_article', 'none']:
#         bot.answer_callback_query(callback_id, "")
#
#
# def show_news_page(bot, parser, chat_id, page, edit_message_id=None):
#     """Show news page with all articles"""
#     if edit_message_id:
#         bot.edit_message_reply_markup(chat_id, edit_message_id)
#
#     html_content = parser.get_news_page(page)
#
#     if not html_content:
#         bot.send_message(chat_id,
#                          "❌ Не удалось загрузить новости.\n"
#                          "Проверьте подключение к интернету и попробуйте снова.",
#                          get_main_menu_keyboard())
#         return
#
#     articles = parser.parse_news_cards(html_content)
#
#     if not articles:
#         bot.send_message(chat_id,
#                          "📭 Новости не найдены.\n\n"
#                          "Попробуйте:\n"
#                          "• Проверить подключение к интернету\n"
#                          "• Нажать <b>🔄 Обновить</b>\n"
#                          "• Попробовать позже\n\n"
#                          "Бот сохранил HTML страницы для отладки.",
#                          get_main_menu_keyboard())
#         return
#
#     # Показываем первую новость
#     show_specific_article(bot, parser, chat_id, page, 0)
#
#     # Информация о странице
#     nav_text = f"📄 Страница {page} - Найдено {len(articles)} новостей"
#     nav_keyboard = get_news_navigation_keyboard(page, has_next=True)
#     bot.send_message(chat_id, nav_text, nav_keyboard)
#
#
# def show_specific_article(bot, parser, chat_id, page, article_index, edit_message_id=None):
#     """Show specific article by index"""
#     if edit_message_id:
#         bot.edit_message_reply_markup(chat_id, edit_message_id)
#
#     # Загружаем новости заново для этой страницы
#     html_content = parser.get_news_page(page)
#     if not html_content:
#         bot.send_message(chat_id, "❌ Не удалось загрузить страницу")
#         return
#
#     articles = parser.parse_news_cards(html_content)
#     if not articles or article_index >= len(articles):
#         bot.send_message(chat_id, "❌ Новость не найдена")
#         return
#
#     article = articles[article_index]
#     caption = format_article_card(article, article_index, len(articles))
#     keyboard = get_article_keyboard(article['url'], page, article_index, len(articles))
#
#     if article.get('image') and article['image'].startswith('http'):
#         bot.send_photo(chat_id, article['image'], caption, keyboard)
#     else:
#         bot.send_message(chat_id, caption, keyboard)
#
#
# def show_full_article(bot, parser, chat_id, article_url):
#     """Show full article content"""
#     content = parser.get_full_article(article_url)
#
#     message = f"<b>📖 Полная новость</b>\n\n{content}"
#
#     back_button = {
#         "inline_keyboard": [
#             [
#                 {"text": "🌐 Открыть на сайте", "url": article_url},
#                 {"text": "🔙 Назад к новостям", "callback_data": "news_page_1"}
#             ]
#         ]
#     }
#
#     if len(message) > 4096:
#         parts = [message[i:i + 4000] for i in range(0, len(message), 4000)]
#         for part in parts[:-1]:
#             bot.send_message(chat_id, part)
#         bot.send_message(chat_id, parts[-1], back_button)
#     else:
#         bot.send_message(chat_id, message, back_button)
#
#
# def main():
#     token = "8453465834:AAEdzYPmtmjayAtTfhitVaiiA3aBtELRDQY"
#     bot = TelegramBot(token)
#     parser = ItProgerParser()
#
#     print("🚀 IT News Parser Bot Started")
#     print("📰 Source: itproger.com/news")
#     print("🤖 Bot: @parsing07_bot")
#     print("📡 Monitoring for messages...")
#
#     last_update_id = None
#
#     while True:
#         try:
#             updates = bot.get_updates(offset=last_update_id)
#
#             if updates and 'result' in updates:
#                 for update in updates['result']:
#                     last_update_id = update['update_id'] + 1
#
#                     if 'message' in update:
#                         user_text = update['message'].get('text', '')
#                         print(f"📨 Message from {update['message']['chat']['id']}: {user_text}")
#                         handle_message(bot, parser, update['message'])
#
#                     elif 'callback_query' in update:
#                         print(f"🔄 Callback: {update['callback_query']['data']}")
#                         handle_callback(bot, parser, update['callback_query'])
#
#             time.sleep(1)
#
#         except KeyboardInterrupt:
#             print("\n🛑 Bot stopped")
#             break
#         except Exception as e:
#             print(f"Error: {e}")
#             time.sleep(5)
#
#
# if __name__ == "__main__":
#     main()