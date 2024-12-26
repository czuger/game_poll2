import asyncio
import logging
from datetime import datetime

from discord import TextChannel

from poll.libs.objects.database import DbConnector
from poll.libs.objects.games import Games

logger = logging.getLogger(__name__)


class GuildNotFound(RuntimeError):
    pass


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

    async def __add_vote(self, game_key: str, vote_diff: int, user_key: str):
        new_vote_document = {
            "gk": game_key,
            "vc": vote_diff,
            "u": user_key,
            "t": datetime.now().isoformat()
        }

        # Update the guild document by pushing a new vote to the "votes" array
        await self.db.db.votes.update_one(
            {"guild_id": self.guild_id},  # Find the document by guild_id
            {"$push": {"votes": new_vote_document}},  # Append new vote to "votes" array
            upsert=True  # If the document doesn't exist, create it
        )

    async def count_vote(self, game_key: str, user_key: str):
        await self.__add_vote(game_key, 1, user_key)

    async def un_count_vote(self, game_key: str, user_key: str):
        await self.__add_vote(game_key, -1, user_key)

    @classmethod
    async def find(cls, db: DbConnector, guild_id: str) -> "Guild":
        """
        Asynchronously finds an existing guild in the database by guild ID.

        Parameters
        ----------
        db : DbConnector
            The database connector instance used for interacting with the database.
        guild_id : str
            The unique identifier of the guild (Discord server).

        Returns
        -------
        Guild
            An instance of the `Guild` class initialized with the guild's data.
        """
        guild = await db.guilds.find_one({"key": guild_id})

        if not guild:
            raise GuildNotFound

        logger.debug(f"In Guild#find, existing_record = {guild}")

        return cls(db, guild_id, guild)

    @classmethod
    async def find_or_create_by_guild_id(cls, db: DbConnector, guild_id: str) -> "Guild":
        """
        Asynchronously finds an existing guild in the database by guild ID or creates a new one.

        Parameters
        ----------
        db : DbConnector
            The database connector instance used for interacting with the database.
        guild_id : str
            The unique identifier of the guild (Discord server).

        Returns
        -------
        Guild
            An instance of the `Guild` class initialized with the guild's data.
        """
        try:
            guild = await cls.find(db, guild_id)
        except GuildNotFound:
            games, poll_default = await Games.get_pre_loaded_games()
            new_record = {
                "key": guild_id,
                "games": games, "poll_default": poll_default
            }
            await db.guilds.insert_one(new_record)
            guild = cls(db, guild_id, new_record)

        return guild

    @classmethod
    async def find_or_create_by_channel(cls, db: DbConnector, channel: TextChannel) -> "Guild":
        """
        Call find_or_create_by_guild_id extracting guild_id from channel

        Parameters
        ----------
        db : DbConnector
            The database object.
        channel : discord.channel.Channel
            The Discord channel object from which the guild ID is extracted.

         Returns
        -------
        Guild
            An instance of the `Guild` class initialized with the guild's data.
        """
        guild_id = str(channel.guild.id)
        return await cls.find_or_create_by_guild_id(db, guild_id)


async def main():
    db = DbConnector()
    db.connect()

    result = await db.votes_history.update_one(
        {"user": "user1"}, {"$push": {"guild1.adg": {"date": datetime.now().isoformat(), "type": "up"}}}, upsert=True)

    print(result)


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        runner.run(main())
