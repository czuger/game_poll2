import json

from poll.libs.misc.project_root import find_project_root


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
            result = json.load(f)
            return result["games"], result["poll_default"]
