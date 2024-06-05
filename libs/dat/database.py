import json

from pymongo import MongoClient

from libs.misc.project_root import find_project_root


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
        root_dir = find_project_root()

        with open(root_dir / "config.json", "r") as f:
            mongo = json.load(f)
            mongo = mongo["mongo"]

        self.db_connection = MongoClient(mongo["server"], 27017, username=mongo["user"], password=mongo["pass"])
        self.db_name = db_name
        self.__initialize_collections()

    def clear_db(self):
        self.db_connection.drop_database(self.db_name)
        self.__initialize_collections()
