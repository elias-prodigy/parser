import json
import urllib3
from bs4 import BeautifulSoup


def page_links():

    # Создаю список страниц содержащих ссылки на статьи
    base_url = 'https://ux.pub/page/'
    list_of_pages = ['https://ux.pub/']
    page_num = 2
    while page_num != 57:
        list_of_pages.append(base_url + str(page_num))
        page_num += 1
    return list_of_pages


def parser():
    global date, header, author, view, tags
    to_json = {}
    article_num = 1
    for url in page_links():

        # Создаем сессию для страницы с перечнем статей
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="lxml")

        # Находим тег div содержащий ссылки на статьи
        article_divs = soup.findAll("div", "post-outer")
        for a in article_divs:
            article = a.find("a", "post-link")
            current_article = article.get("href")

            # Создаем сессию для каждой страницы со статьёй
            http = urllib3.PoolManager()
            response = http.request('GET', current_article)
            soup = BeautifulSoup(response.data, features="lxml")

            # Получаем заголовок статьи
            for h1 in soup.findAll('h1'):
                header = h1.get_text()

            # Находим тег div содержащий мета данные статьи
            meta_details_div = soup.findAll("div", "entry-meta-details")

            # Получаем имя автора статьи
            for li in meta_details_div:
                a = li.find("a", "url")
                author = a.get_text()

            # Получаем дату создания статьи
            for li in meta_details_div:
                d = li.find("li", "meta-date")
                date = d.get_text()

            # Получаем кол-во просмотров статьи
            for li in meta_details_div:
                v = li.find("li", "meta-views")
                view = v.get_text()

            # Получаем SEO информацию
            title = soup.head.title.text
            m = soup.find("meta", attrs={'name': 'description'})
            meta = m.get("content")

            # Получаем теги статьи
            tags_section = soup.find("section", attrs={'class': 'post-section post-tags'})
            tags = []
            if tags_section:
                for t in tags_section.findAll("a"):
                    tags.append(t.get_text())
            else:
                tags = ""

            # Получаем данные из дополнительных полей
            optional_fields = soup.find("div", "send-mistake")
            if optional_fields.a.has_attr("href"):
                source_name = optional_fields.a.get_text()
                source_link = optional_fields.a.get("href")
            else:
                source_name = ""
                source_link = ""

            # Задаем структуру JSON документа
            to_json.update({("article#" + str(article_num)):
                                {"url": current_article,
                                 "header": header,
                                 "author": author,
                                 "creation date": date,
                                 "views": view,
                                 "head_title": title,
                                 "head_meta": meta,
                                 "tags": tags,
                                 "source_name": source_name,
                                 "source_link": source_link}
                            }
                           )
            article_num += 1
    with open('articles.json', 'w') as f:
        json.dump(to_json, f, indent=4, ensure_ascii=False)


parser()
