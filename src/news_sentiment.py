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
    for news in tqdm.tqdm(sentenses_cl.find({}), total=count):
        texts = [sentense['text'] for sentense in news['sentenses']]
        text = ' '.join(texts)

        sentiment = classifier.predict(text)
        sentenses_cl.update_one(
          {"_id": news['_id']},
          {"$set": {'sentiment': sentiment}}
        )


# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Analyze sentiment of all articles in DB')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main(cfg)
