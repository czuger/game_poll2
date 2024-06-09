import logging

import discord
import pymongo

from libs.dat.guild import Guild
from libs.helpers.buttons import make_btn_key

logger = logging.getLogger(__name__)


class PollNotFound(RuntimeError):
    """
    Exception raised when a poll is not found in the database.
    """
    pass


class Poll:
    """
    A class used to represent and manage polls in a MongoDB collection.
    """

    OTHER_BUTTONS = {
        "present_with_key": {"key": "present_with_key", "short": "Clés", "long": "Présent avec les clés", "emoji": "🔑",
                             "style": discord.ButtonStyle.primary},
        "tournament": {"key": "tournament", "short": "Tournoi", "long": "En tournoi", "emoji": "🏅",
                       "style": discord.ButtonStyle.success},
        "orga": {"key": "orga", "short": "Orga", "long": "Organisation", "emoji": "🍺",
                 "style": discord.ButtonStyle.success},
        "other": {"key": "other", "short": "Autre", "long": "Autre activité", "emoji": "♟️",
                  "style": discord.ButtonStyle.success},
        "add": {"key": "add", "short": "Ajouter", "long": "Ajouter un jeu", "emoji": "➕",
                "style": discord.ButtonStyle.red, "action": "add_game"},
    }

    BUTTONS_KEY = "buttons"
    GAMES_KEY = "games"
    OTHERS_KEY = "others"

    POLL_KEY = "key"

    def __init__(self, db: pymongo.database.Database, record: dict):
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
        self.key = record[self.POLL_KEY]

        self.games = None
        self.others = None

        self.__initialize_buttons_data(record)

    def __initialize_buttons_data(self, poll_dict: dict) -> None:
        self.games = poll_dict[self.BUTTONS_KEY][self.GAMES_KEY]
        self.others = poll_dict[self.BUTTONS_KEY][self.OTHERS_KEY]

    async def add_default_games(self, channel) -> None:
        """
        Asynchronously finds an existing poll in the database or creates a new one.

        Parameters
        ----------
        channel : discord.channel.Channel
            The Discord channel object from which the channel ID is extracted.

        Returns
        -------
        The new buttons keys
        """

        print("add_default_games called")
        guild = await Guild.find_or_create(self.db, channel)

        for key, game in guild.games["poll_default"].items():
            game["players"] = []
            self.games[make_btn_key(key, "g")] = game

        for other in self.OTHER_BUTTONS.values():
            other["players"] = []
            self.others[make_btn_key(other["key"], "o")] = other

        await self.db.poll_instances.update_one({"key": self.key}, {"$set": {"buttons.games": self.games}}, upsert=True)
        await self.db.poll_instances.update_one({"key": self.key}, {"$set": {"buttons.others": self.others}},
                                                upsert=True)

    @classmethod
    async def find(cls, db: pymongo.database.Database, channel, create_if_not_exist=False):
        """
        Asynchronously finds an existing poll in the database or creates a new one.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        channel : discord.channel.Channel
            The Discord channel object from which the channel ID is extracted.
        create_if_not_exist : bool
            If the poll does not exist, then we create it.

        Returns
        -------
        Poll
            An instance of the Poll class with the poll's data.
        """
        key = str(channel.id)

        poll_dict = await db.poll_instances.find_one({cls.POLL_KEY: key})
        if poll_dict is None:
            if create_if_not_exist:
                record = {"key": key, cls.BUTTONS_KEY: {cls.GAMES_KEY: {}, cls.OTHERS_KEY: {}}}
                await db.poll_instances.insert_one(record)
                poll = cls(db, record)

                await poll.add_default_games(channel)
            else:
                raise PollNotFound()
        else:
            poll = cls(db, poll_dict)

        return poll

    async def refresh(self):
        poll_dict = await self.db.poll_instances.find_one({self.POLL_KEY: self.key})
        self.__initialize_buttons_data(poll_dict)

    async def toggle_button_id(self, user: discord.User, button_id: str):
        """
        Toggle the buttons status in the poll_instance database object.

        Parameters
        ----------
        user : discord.User
            The Discord user object.
        button_id : str
            The button ID to toggle.
        """
        user_key = str(user.id)

        await self.refresh()

        if button_id[0] == "g":
            button_data = self.games[button_id]
            sub_collection = "games"
        else:
            button_data = self.others[button_id]
            sub_collection = "others"

        if user_key in button_data['players']:
            update_result = await self.db.poll_instances.update_one(
                {'key': self.key}, {'$pull': {f'buttons.{sub_collection}.{button_id}.players': user_key}})
        else:
            update_result = await self.db.poll_instances.update_one(
                {'key': self.key}, {'$push': {f'buttons.{sub_collection}.{button_id}.players': user_key}})

        # Check if the update was successful
        if update_result.modified_count > 0:
            logging.debug(f'{user_key} {button_id} modification done for poll {self.key} success.')
        else:
            logging.debug(f'{user_key} {button_id} modification done for poll {self.key} failed.')
