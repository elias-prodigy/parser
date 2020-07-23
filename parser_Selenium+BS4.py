import json
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def get_articles_links():
    browser = webdriver.Chrome('/home/elias/PycharmProjects/parser/chromedriver')
    browser.get('https://ux.pub/page/56/')
    article_links = []
    to_json = {}
    article_num = 0
    while browser:
        try:
            WebDriverWait(browser, timeout=3)
            article_elems = browser.find_elements(By.CLASS_NAME, "post-outer")
            for elem in article_elems:
                exact_articles = elem.find_elements(By.CLASS_NAME, "post-link")
                for a in exact_articles:
                    article_num += 1
                    article_links.append(a.get_attribute("href"))
                    to_json.update({("article#"+str(article_num)): {"url": a.get_attribute("href")}})
            browser.find_element_by_link_text("Далее").click()
        except NoSuchElementException:
            break
    with open('articles.json', 'w') as f:
        json.dump(to_json, f, indent=2)
    browser.quit()
    return article_links


def parser():
    headers = []
    authors = []
    dates = []
    views = []
    titles = []
    for url in get_articles_links():
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="lxml")

        # Получаем заголовок статьи
        for header in soup.findAll('h1'):
            headers.append(header.get_text())

        # Находим тег div содержащий мета данные статьи
        meta_details_div = soup.findAll("div", "entry-meta-details")

        # Получаем имя автора статьи
        for li in meta_details_div:
            author = li.find("a", "url")
            authors.append(author.get_text())

        # Получаем дату создания статьи
        for li in meta_details_div:
            date = li.find("li", "meta-date")
            dates.append(date.get_text())

        # Получаем кол-во просмотров статьи
        for li in meta_details_div:
            view = li.find("li", "meta-views")
            views.append(view.get_text())

        # for meta in soup.head:
        #     title = meta.find("title")
        #     titles.append()

    # Открываем JSON файл на чтение, затем на запись. Проходим циклом
    # по занчениям главного словаря JSON файла и добавляем из полученных
    # ранее списков новые данные.
    with open('articles.json', 'r') as ff:
        articles = json.load(ff)
    with open('articles.json', 'w') as f:
        v = 0
        for value in articles.values():
            value.update({"header": headers[v]})
            value.update({"author": authors[v]})
            value.update({"creation date": dates[v]})
            value.update({"views": views[v]})
            v += 1
        json.dump(articles, f, indent=4, ensure_ascii=False)


parser()

