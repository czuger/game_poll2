import json

from libs.misc.project_root import find_project_root


class Games:
    """
    A class used to represent and manage games in a MongoDB collection.

    Attributes
    ----------
    games_collection_dict : dict
        A dictionary representing the games collection, where keys are the game keys.
    db : pymongo.database.Database
        The database object.

    Methods
    -------
    __init__(self, db, games_collection_dict)
        Initializes the Games class with a database object and a games collection dictionary.
    get_games(cls, db)
        Class method to asynchronously retrieve all games from the database and create a Games instance.
    get_default_games_keys(cls, db)
        Class method to asynchronously retrieve the keys of default games from the database.
    """

    # TODO : there is no real need for this class.
    # Instead add a dict to guild with two dict : board and miniatures. Only keep short and long param.
    # See inserts_json2.py
    # In the guild object add a "refresh_games" method.
    def __init__(self, db, games_collection_dict):
        """
        Initializes the Games class with a database object and a games collection dictionary.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        games_collection_dict : dict
            A dictionary representing the games collection, where keys are the game keys.
        """
        self.games_collection_dict = games_collection_dict
        self.db = db

    @classmethod
    async def get_games(cls, db):
        """
        Asynchronously retrieves all games from the database and creates a Games instance.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.

        Returns
        -------
        Games
            An instance of the Games class with the games collection data.
        """
        games_collection_dict = {e["key"]: e for e in list(db.games.find())}
        return cls(db, games_collection_dict)

    @classmethod
    async def get_pre_loaded_games(cls):
        """
        Asynchronously retrieves the keys of default games from the database.

        Parameters
        ----------

        Returns
        -------
        list
            A dict of miniatures, board and default games.
        """
        root_directory = find_project_root()

        with open(root_directory / "games" / "games.json") as f:
            return json.load(f)

    def get_miniatures_dict(self) -> dict:
        return {k: v for k, v in self.games_collection_dict.items() if v["type"] == "Miniatures"}

    def get_board_games_dict(self) -> dict:
        return {k: v for k, v in self.games_collection_dict.items() if v["type"] == "Board"}
