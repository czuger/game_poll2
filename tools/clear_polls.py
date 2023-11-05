import json
from pymongo import MongoClient

with open("../config/mongo.json", "r") as f:
    mongo = json.load(f)

client = MongoClient(mongo["server"], 27017, username=mongo["user"], password=mongo["pass"])
db = client["games_database"]
games_collection = db["games"]
polls_collection = db["poll_instance"]

polls_collection.delete_many({})
