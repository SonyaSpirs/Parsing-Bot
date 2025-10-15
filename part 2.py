import json
import re
import socketserver
import urllib.request
import urllib.parse
import html
import ssl
import http.server


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def send_message(self, chat_id, text):
        url = self.base_url + "sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        self._make_request(url, data)

    def _make_request(self, url, data):
        try:
            data_bytes = urllib.parse.urlencode(data).encode('utf-8')
            context = ssl._create_unverified_context()
            req = urllib.request.Request(url, data=data_bytes)
            response = urllib.request.urlopen(req, context=context)
            return response.read().decode('utf-8')
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return None


class ArticleParser:
    @staticmethod
    def parse_article(url):
        try:
            # Добавляем протокол если нужно
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            context = ssl._create_unverified_context()
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response = urllib.request.urlopen(req, context=context)
            html_content = response.read().decode('utf-8')

            return ArticleParser._extract_content(html_content)

        except Exception as e:
            return f"❌ Ошибка при парсинге: {str(e)}"

    @staticmethod
    def _extract_content(html_content):
        # Удаляем скрипты и стили
        html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)

        # Извлекаем заголовок
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Заголовок не найден"
        title = ArticleParser._clean_text(title)

        # Извлекаем мета-описание
        description_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html_content, re.IGNORECASE)
        description = description_match.group(1).strip() if description_match else ""
        description = ArticleParser._clean_text(description)

        # Извлекаем основной контент
        content = ArticleParser._extract_main_content(html_content)

        result = f"<b>📰 Заголовок:</b>\n{title}\n\n"
        if description:
            result += f"<b>📝 Описание:</b>\n{description}\n\n"
        result += f"<b>📄 Содержание:</b>\n{content}"

        return result

    @staticmethod
    def _extract_main_content(html_content):
        # Удаляем все теги, оставляем только текст
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = ArticleParser._clean_text(text)

        # Ограничиваем длину текста для Telegram
        if len(text) > 3000:
            text = text[:3000] + "..."

        return text

    @staticmethod
    def _clean_text(text):
        # Декодируем HTML-сущности
        text = html.unescape(text)
        # Удаляем лишние пробелы и переносы
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text


class BotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Bot @parsing07_bot is running!')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/webhook':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self._handle_update(post_data.decode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_update(self, data):
        try:
            update = json.loads(data)
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')

                bot = TelegramBot("8453465834:AAEdzYPmtmjayAtTfhitVaiiA3aBtELRDQY")
                parser = ArticleParser()

                if text.startswith('/start'):
                    bot.send_message(chat_id,
                                     "👋 Привет! Я бот @parsing07_bot для парсинга статей.\n\n"
                                     "Отправь мне ссылку на статью, и я извлеку из нее текст!\n\n"
                                     "📝 <b>Пример:</b>\nhttps://example.com/article")


                elif text.startswith('/help'):
                    bot.send_message(chat_id,
                                     "📖 <b>Помощь по боту:</b>\n\n"
                                     "• Отправьте ссылку на статью для парсинга\n"
                                     "• Бот извлечет заголовок и основной текст\n"
                                     "• Поддерживаются большинство новостных сайтов\n\n"
                                     "🚀 <b>Просто отправьте ссылку и получите результат!</b>")

                elif self._is_url(text):
                    bot.send_message(chat_id, "⏳ Парсим статью...")
                    article_content = parser.parse_article(text)
                    bot.send_message(chat_id, article_content)

                else:
                    bot.send_message(chat_id,
                                     "❌ Пожалуйста, отправьте валидную ссылку на статью.\n\n"
                                     "<b>Примеры:</b>\n"
                                     "• https://example.com/news/article\n"
                                     "• www.example.com/blog/post\n\n"
                                     "Используйте /help для справки.")

        except json.JSONDecodeError:
            print("Ошибка: полученные данные не являются корректным JSON")
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")

    def _is_url(self, text):
        url_patterns = [
            r'^https?://[^\s/$.?#].[^\s]*$',
            r'^www\.[^\s/$.?#].[^\s]*$'
        ]
        return any(re.match(pattern, text) for pattern in url_patterns)


def set_webhook(token, webhook_url):
    """Установка webhook"""
    bot = TelegramBot(token)
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    data = {"url": webhook_url}
    result = bot._make_request(url, data)
    print(f"Webhook установлен: {result}")


def main():
    PORT = 8080
    TOKEN = "8453465834:AAEdzYPmtmjayAtTfhitVaiiA3aBtELRDQY"

    print(f"🚀 Запуск бота @parsing07_bot на порту {PORT}")
    print("Бот готов к работе!")

    # Запуск HTTP сервера
    with socketserver.TCPServer(("", PORT), BotHandler) as httpd:
        print(f"✅ Сервер запущен на http://localhost:{PORT}")
        print("📝 Для использования на хостинге настройте webhook")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Остановка сервера")


if __name__ == "__main__":
    main()