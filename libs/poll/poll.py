import random

import discord
import pymongo

from libs.guild import Guild


class PollNotFound(RuntimeError):
    """
    Exception raised when a poll is not found in the database.
    """
    pass


class Poll:
    """
    A class used to represent and manage polls in a MongoDB collection.

    Attributes
    ----------
    OTHER_BUTTONS : dict
        A dictionary containing predefined button configurations.
    BUTTONS_KEY : str
        The key used to access buttons in the poll record.
    SELECTIONS_KEY : str
        The key used to access selections in the poll record.
    MESSAGE_ID_KEY : str
        The key used to access the message ID in the poll record.
    key : str
        The unique identifier for the poll.
    selections : dict
        A dictionary containing user selections for the poll.
    buttons : dict
        A dictionary containing button configurations for the poll.
    db : pymongo.database.Database
        The database object.

    Methods
    -------
    __init__(self, db, record)
        Initializes the Poll class with a database object and a record.
    make_btn_key(game_key, typ)
        Static method to create a unique button key.
    find_or_create(cls, db, channel)
        Class method to asynchronously find an existing poll in the database or create a new one.
    find(cls, db, poll_key)
        Class method to asynchronously find a poll in the database.
    get_poll_db_object(self)
        Retrieves the poll record from the database.
    toggle_button_id(self, user, button_id)
        Toggles a user's selection for a given button ID.
    """

    OTHER_BUTTONS = {
        "present_with_key": {"key": "present_with_key", "short": "Clés", "long": "Présent avec les clés", "emoji": "🔑",
                             "style": discord.ButtonStyle.success},
        "tournament": {"key": "tournament", "short": "Tournoi", "long": "En tournoi", "emoji": "🏅",
                       "style": discord.ButtonStyle.danger},
        "other": {"key": "other", "short": "Autre", "long": "Autre activité", "emoji": "♟️",
                  "style": discord.ButtonStyle.success},
        "ajouter": {"key": "ajouter", "short": "Ajouter", "long": "Ajouter un jeu", "emoji": "➕",
                    "style": discord.ButtonStyle.success},
    }

    BUTTONS_KEY = "buttons"
    SELECTIONS_KEY = "selections"
    MESSAGE_ID_KEY = "message_id"

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
        self.key = record["key"]
        self.selections = record.get(self.SELECTIONS_KEY, {})
        self.buttons = record.get(self.BUTTONS_KEY, {})
        self.db = db

    @staticmethod
    def make_btn_key(game_key: str, typ: str):
        """
        Creates a unique button key.

        Parameters
        ----------
        game_key : str
            The key of the game.
        typ : str
            The type of button (e.g., "G" for game, "O" for other).

        Returns
        -------
        str
            A unique button key.
        """
        tmp_gk = game_key[5:-1] if typ == "G" else game_key
        return "BTN" + typ + "_" + tmp_gk + "_" + format(random.randrange(0, 10 ** 9), '09d')

    async def reset_buttons(self, channel) -> None:
        """
        Asynchronously finds an existing poll in the database or creates a new one.

        Parameters
        ----------
        channel : discord.channel.Channel
            The Discord channel object from which the channel ID is extracted.

        Returns
        -------
        """

        guild = await Guild.find_or_create(self.db, channel)

        buttons = {}
        for btn_type in ((guild.games, "G"), (self.OTHER_BUTTONS.keys(), "O")):
            (btn_list, btn_marker) = btn_type

            for k in btn_list:
                buttons[self.make_btn_key(k, btn_marker)] = k

        self.db.poll_instances.update_one({"key": self.key}, {"$set": {self.BUTTONS_KEY: buttons}}, upsert=True)

    @classmethod
    async def find_or_create(cls, db: pymongo.database.Database, channel):
        """
        Asynchronously finds an existing poll in the database or creates a new one.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        channel : discord.channel.Channel
            The Discord channel object from which the channel ID is extracted.

        Returns
        -------
        Poll
            An instance of the Poll class with the poll's data.
        """
        key = str(channel.id)
        guild = await Guild.find_or_create(db, channel)

        try:
            poll = await cls.find(db, key)
        except PollNotFound:
            record = {"key": key, cls.BUTTONS_KEY: {}}
            db.poll_instances.insert_one(record)
            poll = cls(db, record)

            await poll.reset_buttons(channel)

        return poll

    @classmethod
    async def find(cls, db: pymongo.database.Database, poll_key: str):
        """
        Asynchronously finds a poll in the database.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        poll_key : str
            The unique identifier for the poll.

        Returns
        -------
        Poll
            An instance of the Poll class with the poll's data.

        Raises
        ------
        PollNotFound
            If no poll is found with the given key.
        """
        query = {"key": poll_key}
        existing_record = db.poll_instances.find_one(query)

        if not existing_record:
            raise PollNotFound(f"No poll for {poll_key}")

        return cls(db, existing_record)

    def get_poll_db_object(self):
        """
        Retrieves the poll record from the database.

        Returns
        -------
        dict
            The poll record from the database.
        """
        poll_db_object = self.db.poll_instances.find_one({"key": self.key})
        return poll_db_object

    def toggle_button_id(self, user: discord.User, button_id: str):
        """
        Toggles a user's selection for a given button ID.

        Parameters
        ----------
        user : discord.User
            The Discord user object.
        button_id : str
            The button ID to toggle.
        """
        user_key = str(user.id)
        game_key = self.buttons[button_id]

        if game_key not in self.selections:
            self.selections[game_key] = [user_key]
        else:
            if user_key in self.selections[game_key]:
                self.selections[game_key].remove(user_key)
            else:
                self.selections[game_key].append(user_key)

        self.db.poll_instances.update_one({"key": self.key}, {"$set": {self.SELECTIONS_KEY: self.selections}})
