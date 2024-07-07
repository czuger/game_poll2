import json

from motor.motor_asyncio import AsyncIOMotorClient

from libs.misc.project_root import find_project_root


class DbConnector:
    """
    A class used to represent a connection to a MongoDB database.

    Attributes
    ----------
    db : pymongo.database.Database
        The database object.
    games : pymongo.collection.Collection
        The games collection in the database.
    poll_instances : pymongo.collection.Collection
        The polls collection in the database.
    guilds : pymongo.collection.Collection
        The guilds collection in the database.
    admins : pymongo.collection.Collection
        The admins collection in the database.
    db_connection : pymongo.MongoClient
        The MongoDB client connection.
    db_name : str
        The name of the database.

    Methods
    -------
    __initialize_collections()
        Initializes the collections in the database.
    connect(db_name="games_database")
        Connects to the MongoDB database with the given database name.
    clear_db()
        Clears the database by dropping it and reinitializing the collections.
    """

    def __init__(self):
        """
        Initializes the DbConnector with default values.
        """
        self.db = None
        self.games = None
        self.poll_instances = None
        self.guilds = None
        self.admins = None

        self.db_connection = None
        self.db_name = None

    def __initialize_collections(self):
        """
        Initializes the collections in the database.
        """
        self.db = self.db_connection[self.db_name]

        self.games = self.db["games"]
        self.poll_instances = self.db["poll_instances"]
        self.guilds = self.db["guilds"]
        self.admins = self.db["admins"]
        self.votes_history = self.db["votes_history"]

    def connect(self, db_name="games_database"):
        """
        Connects to the MongoDB database with the given database name.

        Parameters
        ----------
        db_name : str, optional
            The name of the database to connect to (default is "games_database").
        """
        root_dir = find_project_root()

        with open(root_dir / "config.json", "r") as f:
            mongo = json.load(f)
            mongo = mongo["mongo"]

        self.db_connection = AsyncIOMotorClient(mongo["server"], 27017, username=mongo["user"], password=mongo["pass"])
        self.db_name = db_name
        self.__initialize_collections()

    def clear_db(self):
        """
        Clears the database by dropping it and reinitializing the collections.
        """
        self.db_connection.drop_database(self.db_name)
        self.__initialize_collections()
