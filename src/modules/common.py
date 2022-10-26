# Общие утилиты для всех скриптов

from pymongo import MongoClient
import os
import string

MONGO_CONN_STR = "mongodb://user:pass@localhost/test"

punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~«»”—'
TRANSLATION = str.maketrans('', '', punctuation)

def get_db():
    """Подключается к MongoDB и возвращает подключение к нужной базе"""
    client = MongoClient(MONGO_CONN_STR)
    return client['test']

def clear_lemma(text):
    """Приводит текст (текст факта) к единому виду"""
    return text \
        .lower() \
        .translate(TRANSLATION) \
        .replace(' ', '_')
