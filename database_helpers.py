import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
db_collection_name = os.getenv('DATABASE_NAME')

def connect():
    client = MongoClient(db_url)
    return client['test_data']

def insert(item, collection):
    if collection.count_documents({'_id': item['_id']}, limit = 1) == 0:
        collection.insert_one(item)
        return True

    return False