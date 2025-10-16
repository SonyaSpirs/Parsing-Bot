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
            print(f"🔄 Парсинг URL: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Упрощенный поиск статей - ищем любые карточки с ссылками
            article_blocks = soup.find_all('a', href=True)

            for block in article_blocks:
                if len(articles) >= 5:  # Ограничиваем 5 статьями
                    break

                href = block['href']
                # Фильтруем только статьи
                if '/news/' in href and href != '/news/':
                    article = self._parse_article_block(block)
                    if article and article['title'] and article['title'] != "Без заголовка":
                        articles.append(article)

            # Если не нашли статей, пробуем альтернативный метод
            if not articles:
                articles = self._alternative_parse(soup)

            print(f"✅ Найдено статей: {len(articles)}")
            return articles

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return []

    def _parse_article_block(self, block):
        """Парсит отдельный блок статьи"""
        try:
            # Заголовок
            title_elem = (block.find('h2') or
                          block.find('h3') or
                          block.find('h1') or
                          block.find('span') or
                          block)
            title = title_elem.get_text().strip() if title_elem else "Без заголовка"

            # Ссылка
            link = block['href']
            if link and not link.startswith('http'):
                link = f"https://itproger.com{link}" if link.startswith('/') else f"https://itproger.com/{link}"

            # Изображение
            img_elem = block.find('img')
            img_url = img_elem.get('src') if img_elem else ""
            if img_url and not img_url.startswith('http'):
                img_url = f"https://itproger.com{img_url}" if img_url.startswith('/') else img_url

            # Описание (ищем в родительском элементе)
            parent = block.parent
            desc_elem = (parent.find('p') if parent else None)
            description = desc_elem.get_text().strip() if desc_elem else "Описание недоступно"

            # Обрезаем длинное описание
            if len(description) > 200:
                description = description[:200] + "..."

            # Обрезаем длинный заголовок
            if len(title) > 100:
                title = title[:100] + "..."

            return {
                'title': title,
                'description': description,
                'image_url': img_url,
                'link': link,
                'full_content': None
            }

        except Exception as e:
            print(f"❌ Ошибка парсинга блока: {e}")
            return None

    def _alternative_parse(self, soup):
        """Альтернативный метод парсинга"""
        articles = []
        try:
            # Ищем по классам
            for elem in soup.find_all(class_=True):
                class_names = ' '.join(elem.get('class', []))
                if any(word in class_names.lower() for word in ['article', 'news', 'post', 'card']):
                    title_elem = elem.find(['h1', 'h2', 'h3', 'h4'])
                    link_elem = elem.find('a', href=True)

                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        link = link_elem['href']

                        if link and not link.startswith('http'):
                            link = f"https://itproger.com{link}" if link.startswith(
                                '/') else f"https://itproger.com/{link}"

                        articles.append({
                            'title': title,
                            'description': "Описание недоступно",
                            'image_url': "",
                            'link': link,
                            'full_content': None
                        })

                        if len(articles) >= 5:
                            break
        except Exception as e:
            print(f"❌ Ошибка альтернативного парсинга: {e}")

        return articles

    def get_full_content(self, article_url):
        """Получает полное содержимое статьи"""
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Ищем основной контент
            content_elem = (soup.find('article') or
                            soup.find('div', class_=re.compile(r'content|post-content|article-content')) or
                            soup.find('main'))

            if content_elem:
                # Удаляем ненужные элементы
                for elem in content_elem.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    elem.decompose()

                # Форматируем код блоки для Markdown
                for code_block in content_elem.find_all('pre'):
                    code_block.replace_with(f"\n```\n{code_block.get_text()}\n```\n")

                text = content_elem.get_text().strip()
                return text[:2000] + "..." if len(text) > 2000 else text
            else:
                return "Полное содержимое статьи недоступно"

        except Exception as e:
            print(f"❌ Ошибка получения полного контента: {e}")
            return "Не удалось загрузить полное содержимое статьи"