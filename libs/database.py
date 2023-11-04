import json

from pymongo import MongoClient

# Configuration de la connexion MongoDB

db = None
games_collection = None
polls_collection = None


def initialize_db():
    global db
    global games_collection
    global polls_collection

    with open("mongo.json", "r") as f:
        mongo = json.load(f)

    client = MongoClient(mongo["server"], 27017, username=mongo["user"], password=mongo["pass"])
    db = client["games_database"]
    games_collection = db["games"]
    polls_collection = db["poll_instances"]
