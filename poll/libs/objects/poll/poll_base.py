from discord import TextChannel

from poll.libs.misc.constants import KEY
from poll.libs.objects.database import DbConnector


class PollNotFound(RuntimeError):
    """
    Exception raised when a poll is not found in the database.
    """
    pass


class PollBase:

    def __init__(self, db: DbConnector, channel, record: dict):
        """
        Initializes the Poll class with a database object and a record.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        record : dict
            A dictionary containing the poll's record from the database.
        """
        self.db = db
        self.key = record[KEY]

        self.poll_record = record

        self.channel = channel

    async def remove_poll_from_db(self):
        await self.db.poll_instances.delete_one({"key": self.key})

    async def refresh(self):
        """
        Refreshes the poll data from the database. Mostly used in tests.
        """
        record = await self.db.poll_instances.find_one({KEY: self.key})
        self.poll_record = record

    async def find(cls, db: DbConnector, channel: TextChannel):
        """
        Asynchronously finds an existing poll in the database or creates a new one.

        Parameters
        ----------
        db : DbConnector
            The database object.
        channel : TextChannel
            The Discord channel object from which the channel ID is extracted.

        Returns
        -------
        Poll
            An instance of the Poll class with the poll's data.
        """
        key = str(channel.id)

        record = await db.poll_instances.find_one({KEY: key})
        if record is None:
            raise PollNotFound()

        return cls(db, channel, record)
