import json
import os.path

from pymongo import MongoClient


class DbConnector:
    def __init__(self):
        self.db = None
        self.games = None
        self.polls = None
        self.guilds = None

        self.db_connection = None
        self.db_name = None

        self.admins = None

    def __initialize_collections(self):
        self.db = self.db_connection[self.db_name]

        self.games = self.db["games"]
        self.polls = self.db["poll_instances"]
        self.guilds = self.db["guilds"]

        self.admins = self.db["admins"]

    def connect(self, db_name="games_database"):
        mongo_file = "config/mongo.json"
        if not os.path.exists(mongo_file):
            mongo_file = "../" + mongo_file

        with open(mongo_file, "r") as f:
            mongo = json.load(f)

        self.db_connection = MongoClient(mongo["server"], 27017, username=mongo["user"], password=mongo["pass"])
        self.db_name = db_name
        self.__initialize_collections()

    def clear_db(self):
        self.db_connection.drop_database(self.db_name)
        self.__initialize_collections()
