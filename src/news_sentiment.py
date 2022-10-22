import argparse
import tqdm
import pymongo
from modules import common
from sentiment import SentimentAnalyzer

def main(cfg):
    classifier = SentimentAnalyzer()
    db = common.get_db()
    sentenses_cl = db['sentenses']

    count = sentenses_cl.count_documents({})
    view = sentenses_cl.find({})
    for news in tqdm.tqdm(view, total=count):
        # Определяем тональность
        sentiments = [classifier.predict(sentence['text']) for sentence in news['sentenses']]

        # Формируем запрос для обновления базы
        update_query = {f'sentenses.{i}.sentiment': sentiment for i, sentiment in enumerate(sentiments)}
        sentenses_cl.update_one(
            {'_id': news['_id']},
            {'$set': update_query})


# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Analyze sentiment of all articles in DB')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main(cfg)
