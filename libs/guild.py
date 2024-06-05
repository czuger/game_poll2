from libs.games import Games


class Guild:
    """
    A class used to represent and manage a guild in a MongoDB collection.

    Attributes
    ----------
    key : str
        The unique identifier for the guild.
    games : list
        A list of games associated with the guild.
    db : pymongo.database.Database
        The database object.

    Methods
    -------
    __init__(self, db, record)
        Initializes the Guild class with a database object and a record.
    find_or_create(cls, db, channel)
        Class method to asynchronously find an existing guild in the database or create a new one.
    """

    def __init__(self, db, record):
        """
        Initializes the Guild class with a database object and a record.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        record : dict
            A dictionary containing the guild's record from the database.
        """
        self.key = record["key"]
        self.games = record["games"]
        self.db = db

    @classmethod
    async def find_or_create(cls, db, channel):
        """
        Asynchronously finds an existing guild in the database or creates a new one.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        channel : discord.channel.Channel
            The Discord channel object from which the guild ID is extracted.

        Returns
        -------
        Guild
            An instance of the Guild class with the guild's data.
        """
        key = str(channel.guild.id)
        query = {"key": key}
        existing_record = db.guilds.find_one(query)

        if not existing_record:
            existing_record = {
                "key": key,
                "games": (await Games.get_default_games_keys(db))[0:20]
                # We can't show more than 20 games due to Discord limitations
            }
            db.guilds.insert_one(existing_record)

        return cls(db, existing_record)
