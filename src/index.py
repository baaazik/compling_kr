from flask import Flask
import flask

app = Flask(__name__)

@app.route('/')
@app.route('/news')
def news():
    return flask.render_template('news.html', title='Новости')

@app.route('/facts')
def facts():
    return flask.render_template('facts.html', title='Факты')

@app.route('/sentiment')
def sentiment():
    return flask.render_template('sentiment.html', title='Тональность')

if __name__ == '__main__':
    app.run(debug=True)
