from pymongo import MongoClient
from config import config
client = MongoClient(config.MONGO_URI)
db = client[config.DB]
collection = db[config.COLLECTION]
