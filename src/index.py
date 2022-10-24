from flask import Flask
from flask import render_template, request
import pymongo
import math

from modules import common

ITEMS_PER_PAGE = 100

app = Flask(__name__)

# Определяет номер страницы на основе аргументов
def get_page_index():
    try:
        return int(request.args.get('page', 0))
    except ValueError:
        return 0

# Дополняет запрос к базе пагинацией (берет записи только для нужной странице)
def paginate(data):
    page = get_page_index()
    data = data.skip(page * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)
    total = data.count()
    pages = math.ceil(total / float(ITEMS_PER_PAGE))
    return data, pages

@app.route('/')
@app.route('/news')
def news():
    db = common.get_db()
    news_cl = db['news']
    page = get_page_index()

    news = news_cl.find({}).sort([('date', pymongo.DESCENDING)])
    news, pages = paginate(news)

    return render_template('news.html', title='Новости', news=news, pages=pages, curpage=page)

@app.route('/facts')
def facts():
    return render_template('facts.html', title='Факты')

@app.route('/sentiment')
def sentiment():
    return render_template('sentiment.html', title='Тональность')

if __name__ == '__main__':
    app.run(debug=True)
