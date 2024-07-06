import logging

from libs.dat.database import DbConnector
from libs.dat.games import Games

logger = logging.getLogger(__name__)


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

    def __init__(self, db: DbConnector, guild_id, record):
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

        self.games = None
        self.miniatures = None
        self.boards = None
        self.poll_default = None

        self.db = db
        self.guild_id = guild_id

        self.set_shortcuts(record)

    def set_shortcuts(self, record):
        self.games = record["games"]
        self.poll_default = record["poll_default"]

    async def synchronize(self):
        query = {"key": self.guild_id}
        record = await self.db.guilds.find_one(query)
        self.set_shortcuts(record)

    async def remove_poll_from_db(self):
        await self.db.guilds.delete_one({"key": self.key})

    @classmethod
    async def find_or_create(cls, db: DbConnector, channel):
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
        guild_id = str(channel.guild.id)
        query = {"key": guild_id}
        existing_record = await db.guilds.find_one(query)

        if not existing_record:
            games, poll_default = await Games.get_pre_loaded_games()
            existing_record = {
                "key": guild_id,
                "games": games, "poll_default": poll_default
            }
            await db.guilds.insert_one(existing_record)

        logger.debug(f"In Guild#find_or_create, existing_record = {existing_record}")

        return cls(db, guild_id, existing_record)
