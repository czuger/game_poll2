import logging
from copy import copy
from typing import Optional

import discord

from poll.libs.interfaces.helpers.buttons import make_btn_key
from poll.libs.misc.constants import KEY, LONG_NAME
from poll.libs.misc.logging.set_logging import POLLS_LOG_NAME
from poll.libs.objects.database import DbConnector
from poll.libs.objects.guild import Guild

logger = logging.getLogger(POLLS_LOG_NAME)


class PollNotFound(RuntimeError):
    """
    Exception raised when a poll is not found in the database.
    """
    pass


class ButtonIdNotInPoll(RuntimeError):
    """
    Exception raised when a button id is not found in the poll other or games dictionaries.
    """

    def __init__(self, button_id: str, games: dict):
        message = f"{button_id} not found in {games}"
        super().__init__(message)


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

    async def refresh(self):
        """
        Refreshes the poll data from the database. Mostly used in tests.

        Fetches the latest poll data associated with the current poll key and
        reinitializes the poll instance with the updated data.
        """
        poll_dict = await self.db.poll_instances.find_one({self.POLL_KEY: self.key})
        self.__initialize_poll(poll_dict)

    def get_games_keys_set(self) -> set:
        """
        Retrieves a set of all game keys associated with the current poll. Mostly used in tests.

        Returns
        -------
        set of str
            A set containing the unique keys of all games in the poll, in the format of game identifiers,
            e.g., {'adg', 'bolt_action', 'frostgrave', 'malifaux', 'saga'}.

        """
        return set([e[KEY] for e in self.games.values()])

    def get_games_button_ids_list(self) -> list:
        """
        Retrieves a list of all button IDs associated with the current poll. Mostly used for tests.

        Returns
        -------
        list of str
            A list containing the button IDs of all games in the poll, in the format of unique
            identifiers, e.g., ['g_adg_009828688', 'g_bolt_action_871796500',
            'g_frostgrave_839799436', 'g_malifaux_594148779', 'g_saga_084217325'].
        """
        return list(self.games.keys())

    def button_id_to_element_key(self, button_id: str) -> str:
        """
        Converts a button ID to its corresponding element key.

        Parameters
        ----------
        button_id : str
            The button ID to be mapped to an element key.

        Returns
        -------
        str
            The element key associated with the given button ID.

        Raises
        ------
        ButtonIdNotPoll
            If the button ID is not found in the poll's data.
        """
        data_dict = self.others if button_id in self.others else self.games
        if button_id not in data_dict:
            raise ButtonIdNotInPoll(button_id, self.games)

        return data_dict[button_id][KEY]

    async def add_game(self, game_key: str) -> (bool, Optional[str]):
        """
        Adds a game to the poll, allowing users to vote for it.

        Parameters
        ----------
        game_key : str
            The unique identifier for the game to be added to the poll.

        Returns
        -------
        tuple
            A tuple containing:
            - bool: True if the game was successfully added, False if it already exists in the poll.
            - Optional[str]: The long name of the game if added, or None if the game already exists.

        """
        if game_key not in self.get_games_keys_set():
            guild = await Guild.find(self.db, str(self.channel.guild.id))

            game = copy(guild.games[game_key])
            logger.debug(f"In Poll#add_game : game = {game}")

            new_btn_key = make_btn_key(game_key, "g")
            logger.debug(f"In Poll#add_game : new_btn_key = {new_btn_key}")

            self.games[new_btn_key] = game
            await self.db.poll_instances.update_one({"key": self.key},
                                                    {"$set": {f"buttons.games.{new_btn_key}": game}})

            return True, game[LONG_NAME]
        else:
            return False, None

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

        logger.debug("add_default_games called")
        guild = await Guild.find_or_create_by_channel(self.db, channel)

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
        logger.debug(channel)
        return cls(db, channel, poll_record)
