import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

def connect():
    print('> Connecting to DB!')
    client = MongoClient(db_url)
    return client['test_data']