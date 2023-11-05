import uuid

import discord

from libs.guild import Guild


class PollNotFound(RuntimeError):
    pass


class Poll:
    OTHER_BUTTONS = {
        "present_with_key": {"key": "present_with_key", "short": "Clés", "long": "Présent avec les clés", "emoji": "🔑",
                             "style": discord.ButtonStyle.success},
        "tournament": {"key": "tournament", "short": "Tournoi", "long": "En tournoi", "emoji": "🏅",
                       "style": discord.ButtonStyle.danger},
        "other": {"key": "other", "short": "Autre", "long": "Autre activité", "emoji": "♟️",
                  "style": discord.ButtonStyle.success},
    }

    SELECTIONS_KEY = "selections"
    MESSAGE_ID_KEY = "message_id"

    def __init__(self, db, record):
        self.key = record["key"]
        self.games = record["games"]
        self.others = record["others"]

        if self.SELECTIONS_KEY in record:
            self.selection = record[self.SELECTIONS_KEY]
        else:
            self.selection = []

        self.db = db

    @classmethod
    async def find_or_create(cls, db, channel):
        key = str(channel.id)

        guild = await Guild.find_or_create(db, channel)

        try:
            poll = await cls.find(db, key)
        except PollNotFound:
            games = {}
            for k in guild.games:
                games[str(uuid.uuid4())] = k

            others = {}
            for k in cls.OTHER_BUTTONS:
                others[str(uuid.uuid4())] = k

            existing_record = {
                "key": key,
                "games": games,
                "others": others
            }

            db.polls.insert_one(existing_record)
            poll = cls(db, existing_record)

        return poll

    @classmethod
    async def find(cls, db, poll_key):
        query = {"key": poll_key}
        existing_record = db.polls.find_one(query)

        if not existing_record:
            raise PollNotFound(f"No poll for {poll_key}")

        return cls(db, existing_record)

    def get_poll_db_object(self):
        poll_db_object = self.db.polls.find_one({"key": self.key})
        return poll_db_object

    def toggle_button_id(self, user, button_id):
        user_key = str(user.id)

        poll_db_obj = self.get_poll_db_object()

        if self.SELECTIONS_KEY in poll_db_obj:
            selections = poll_db_obj[self.SELECTIONS_KEY]
        else:
            selections = {}

        if button_id not in selections:
            selections[button_id] = [user_key]
        else:
            if user_key in selections[button_id]:
                selections[button_id].remove(user_key)
            else:
                selections[button_id].append(user_key)

        self.db.polls.update_one({"key": self.key}, {"$set": {self.SELECTIONS_KEY: selections}})
