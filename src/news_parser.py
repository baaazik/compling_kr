import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import locale
from pymongo import MongoClient
import requests
import time
import tqdm
import traceback

import modules.common

TOTAL_PAGES = 10
POSTS_PER_PAGE = 40
DELAY = 0.5

# Загружает список новостей
def load_news(page):
    url = f'https://vlg-media.ru/wp-admin/admin-ajax.php?posts_per_page={POSTS_PER_PAGE}&page={page}&offset=0&order=DESC&orderby=date&action=alm_get_posts'
    r = requests.get(url)
    return r.json()

# Парсит список новостей
def parse_news_list(html):
    # Парсим HTML
    soup = BeautifulSoup(html, 'lxml')
    news_tags = soup.find_all('li', class_='alm-item')

    parsed_news = []

    # Проходим по всем новостям
    for news_tag in news_tags:

        # Находим элемементы в разметке новости
        link_tag = news_tag.find('a')
        date_tag = news_tag.find('p', class_='entry-meta')
        date = datetime.strptime(date_tag.text, '%d %B, %Y')
        url =link_tag['href']
        # Добавляем запись
        news_item = {
            '_id': url, # используем URL в качестве ID
            'title': link_tag.text,
            'url': url,
            'date': date
        }
        parsed_news.append(news_item)

    return parsed_news

# Получает список новостей
def get_news_list(page):
    json = load_news(page)
    html = json['html']
    news = parse_news_list(html)
    return news

# Загружает страницу новости
def load_news_details(url):
    r = requests.get(url)
    return r.text

# Парсит страницу новости
def parse_news_details(news, html):
    soup = BeautifulSoup(html, 'lxml')
    article_tag = soup.find('article')
    short_text_tag = article_tag.find('p', class_='uk-text-lead')
    text_tag = article_tag.find('div', class_='entry-content')

    # Текст разделен на несколько тегов <p>
    # Найдем все и соединим
    p_tags = text_tag.find_all('p')
    p_texts = [p.text for p in p_tags]
    text = ' '.join(p_texts)

    news['short_text'] = short_text_tag.text
    news['text'] = text

# Поулчает дополнительную информацию о новости со страницы новости
def get_news_details(news):
    html = load_news_details(news['url'])
    parse_news_details(news, html)

# Получает новости с заданной страницы
def get_news(page):
    news = get_news_list(page)
    for item in news:
        time.sleep(DELAY)
        get_news_details(item)

    return news

def insert_or_update(collection, news):
    for item in news:
        collection.update_one(
            {"_id": item['_id']},
            {'$set': item},
            upsert=True
        )

def main():
    # Устанавливаем русскую локаль для парсинга даты
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    db = common.get_db()
    news_cl = db['news']

    for page in tqdm.tqdm(range(cfg.pages)):
        try:
            news = get_news(page)
            insert_or_update(news_cl, news)
        except:
            print(traceback.format_exc())


# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Parse news from web site')
    parser.add_argument('-p', '--pages', type=str, default=TOTAL_PAGES,
        help='Number of pages to parse')

    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main()
