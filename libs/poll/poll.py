import logging
from copy import copy

import discord

from libs.dat.database import DbConnector
from libs.dat.guild import Guild
from libs.helpers.buttons import make_btn_key
from libs.misc.set_logging import POLLS_LOG_NAME

logger = logging.getLogger(POLLS_LOG_NAME)


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
                             "style": discord.ButtonStyle.green},
        # "tournament_orga": {"key": "tournament_orga", "short": "Tournoi/Orga",
        #                     "long": "En tournoi ou en orga de tournoi", "emoji": "🍺",
        #                     "style": discord.ButtonStyle.success},
        "other": {"key": "other", "short": "Autre", "long": "Autre activité", "emoji": "♟️",
                  "style": discord.ButtonStyle.blurple},
        "away": {"key": "away", "short": "Absent", "long": "Absent", "emoji": "⛱️",
                 "style": discord.ButtonStyle.blurple},
        "add": {"key": "add", "short": "Ajouter", "long": "Ajouter un jeu", "emoji": "🧩",
                "style": discord.ButtonStyle.grey, "action": "add_game"},
    }

    BUTTONS_KEY = "buttons"
    GAMES_KEY = "games"
    OTHERS_KEY = "others"
    VOTES_KEY = "votes"

    POLL_KEY = "key"

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
        self.key = record[self.POLL_KEY]

        self.games = None
        self.others = None
        self.votes = {}

        self.channel = channel

        self.__initialize_poll(record)

    def __initialize_poll(self, poll_dict: dict) -> None:
        self.games = poll_dict[self.BUTTONS_KEY][self.GAMES_KEY]
        self.others = poll_dict[self.BUTTONS_KEY][self.OTHERS_KEY]

        if self.VOTES_KEY in poll_dict:
            self.votes = poll_dict[self.VOTES_KEY]

    async def remove_poll_from_db(self):
        await self.db.poll_instances.delete_one({"key": self.key})

    async def reset_votes(self):
        await self.db.poll_instances.update_one({"key": self.key}, {'$set': {'votes': {}}})

    async def refresh(self):
        """Refresh data from poll"""
        poll_dict = await self.db.poll_instances.find_one({self.POLL_KEY: self.key})
        self.__initialize_poll(poll_dict)

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

        for element_key in guild.poll_default:
            game = copy(guild.games[element_key])
            self.games[make_btn_key(element_key, "g")] = game

        for other in self.OTHER_BUTTONS.values():
            self.others[make_btn_key(other["key"], "o")] = other

        await self.db.poll_instances.update_one({"key": self.key}, {"$set": {"buttons.games": self.games}}, upsert=True)
        await self.db.poll_instances.update_one({"key": self.key}, {"$set": {"buttons.others": self.others}},
                                                upsert=True)

    @classmethod
    async def find(cls, db: DbConnector, channel, create_if_not_exist=False):
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
                poll = cls(db, channel, record)

                await poll.add_default_games(channel)
            else:
                raise PollNotFound()
        else:
            poll = cls(db, channel, poll_dict)

        return poll

    @classmethod
    async def get_bot_at_restart(cls, bot, db: DbConnector, poll_record):
        print(poll_record[cls.POLL_KEY])
        channel = await bot.fetch_channel(poll_record[cls.POLL_KEY])
        print(channel)
        return cls(db, channel, poll_record)

    async def toggle_button_id(self, interaction: discord.Interaction, button_id: str):
        """
        Toggle the votes status for a user.
        """
        user_key = str(interaction.user.id)
        logger.debug(f"For poll {self.key}, toggle_button_call {button_id} by {user_key}")

        # Define the query to search for the button_id in either buttons.games or buttons.others
        button_key_query = {
            '$or': [
                {f'buttons.games.{button_id}': {'$exists': True}},
                {f'buttons.others.{button_id}': {'$exists': True}}
            ]
        }
        # Project the results to include only the button data
        button_key_projection = {
            f'buttons.games.{button_id}': 1,
            f'buttons.others.{button_id}': 1
        }
        result = await self.db.poll_instances.find_one(button_key_query, button_key_projection)
        logger.debug(f"For poll {self.key}, button find in poll {result}")

        if result:
            guild = await Guild.find_or_create(self.db, self.channel)

            element_key = result["buttons"]["games"].get(button_id, {}).get("key") or result["buttons"]["others"].get(
                button_id, {}).get("key")

            logger.debug(f"For poll {self.key}, element_key = {element_key}")

            query = {f'votes.{element_key}': user_key, 'key': self.key}
            game_voted = await self.db.poll_instances.find_one(query)
            logger.debug(f"For poll {self.key}, game_voted = {game_voted}")

            if game_voted:
                update_result = await self.db.poll_instances.update_one(
                    {'key': self.key}, {'$pull': {f'votes.{element_key}': user_key}})

                await guild.un_count_vote(element_key, user_key)
            else:
                update_result = await self.db.poll_instances.update_one(
                    {'key': self.key}, {'$push': {f'votes.{element_key}': user_key}})

                await guild.count_vote(element_key, user_key)

            if update_result.modified_count > 0:
                logger.debug(f'{user_key} {button_id} modification done for poll {self.key} success.')
            else:
                logger.debug(f'{user_key} {button_id} modification done for poll {self.key} failed.')
                logger.debug(f'{update_result}')

        else:
            logger.critical(f"{button_id} not found for poll {self.key}")
