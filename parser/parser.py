from pymongo import MongoClient

CONN = "mongodb://user:pass@localhost/test"
client = MongoClient(CONN)
db = client['test']
collection = db['news']

item = {
    'name': 'test'
}

collection.insert(item)
