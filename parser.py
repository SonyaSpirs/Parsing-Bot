import requests
from bs4 import BeautifulSoup
from config import ITPROGER_URL, HEADERS
import re


class ITProgerParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_articles(self, page=1):
        """Парсит статьи с указанной страницы"""
        try:
            url = f"{ITPROGER_URL}/{page}" if page > 1 else ITPROGER_URL
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Поиск блоков со статьями
            article_blocks = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'article|news|post'))

            for block in article_blocks[:10]:  # Ограничиваем 10 статьями
                article = self._parse_article_block(block)
                if article and article['title']:
                    articles.append(article)

            return articles

        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            return []

    def _parse_article_block(self, block):
        """Парсит отдельный блок статьи"""
        try:
            # Заголовок
            title_elem = (block.find('h2') or
                          block.find('h3') or
                          block.find('h1') or
                          block.find('a', class_=re.compile(r'title')))
            title = title_elem.get_text().strip() if title_elem else "Без заголовка"

            # Ссылка
            link_elem = block.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https://itproger.com{link}" if link.startswith('/') else f"https://itproger.com/{link}"

            # Изображение
            img_elem = block.find('img')
            img_url = img_elem.get('src') if img_elem else ""
            if img_url and not img_url.startswith('http'):
                img_url = f"https://itproger.com{img_url}" if img_url.startswith('/') else img_url

            # Описание
            desc_elem = (block.find('p') or
                         block.find('div', class_=re.compile(r'content|description|text')))
            description = desc_elem.get_text().strip() if desc_elem else "Описание недоступно"

            # Обрезаем длинное описание
            if len(description) > 200:
                description = description[:200] + "..."

            return {
                'title': title,
                'description': description,
                'image_url': img_url,
                'link': link,
                'full_content': None  # Будет загружаться по требованию
            }

        except Exception as e:
            print(f"Ошибка парсинга блока: {e}")
            return None

    def get_full_content(self, article_url):
        """Получает полное содержимое статьи"""
        try:
            response = self.session.get(article_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Ищем основной контент
            content_elem = (soup.find('article') or
                            soup.find('div', class_=re.compile(r'content|post-content|article-content')))

            if content_elem:
                # Удаляем ненужные элементы
                for elem in content_elem.find_all(['script', 'style', 'nav', 'footer']):
                    elem.decompose()

                # Форматируем код блоки для Markdown
                for code_block in content_elem.find_all('pre'):
                    code_block.replace_with(f"\n```\n{code_block.get_text()}\n```\n")

                text = content_elem.get_text().strip()
                return text[:3000] + "..." if len(text) > 3000 else text
            else:
                return "Полное содержимое статьи недоступно"

        except Exception as e:
            print(f"Ошибка получения полного контента: {e}")
            return "Не удалось загрузить полное содержимое статьи"