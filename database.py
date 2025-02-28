from pymongo import MongoClient
from config import config
client = MongoClient(config.MONGO_URI)
db = client[config.DB]
collection = db[config.COLLECTION]
users_collection = db[config.USER_COLLECTION]  # 存储用户信息的 Collection
