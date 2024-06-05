class Games:
    """
    A class used to represent and manage games in a MongoDB collection.

    Attributes
    ----------
    dict : dict
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
        self.dict = games_collection_dict
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
    async def get_default_games_keys(cls, db):
        """
        Asynchronously retrieves the keys of default games from the database.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.

        Returns
        -------
        list
            A list of keys for the default games.
        """
        return [e["key"] for e in list(db.games.find()) if e.get("default") == True]
