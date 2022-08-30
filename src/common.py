# Общие утилиты для всех скриптов

from pymongo import MongoClient

MONGO_CONN_STR = "mongodb://user:pass@localhost/test"

def get_db():
    """Подключается к MongoDB и возвращает подключение к нужной базе"""
    client = MongoClient(MONGO_CONN_STR)
    return client['test']
