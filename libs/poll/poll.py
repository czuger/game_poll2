import random

import discord

from libs.dat.guild import Guild


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

    BUTTONS_KEY = "buttons"
    SELECTIONS_KEY = "selections"
    MESSAGE_ID_KEY = "message_id"

    def __init__(self, db, record):
        self.key = record["key"]

        self.selections = record.get(self.SELECTIONS_KEY, {})
        self.buttons = record.get(self.BUTTONS_KEY, {})

        self.db = db

    @staticmethod
    def make_btn_key(game_key, typ):
        tmp_gk = game_key[5:-1] if typ == "G" else game_key
        return "BTN" + typ + "_" + tmp_gk + "_" + format(random.randrange(0, 10 ** 9), '09d')

    @classmethod
    async def find_or_create(cls, db, channel):
        key = str(channel.id)

        guild = await Guild.find_or_create(db, channel)

        try:
            poll = await cls.find(db, key)
        except PollNotFound:
            buttons = {}
            for btn_type in ((guild.games, "G"), (cls.OTHER_BUTTONS.keys(), "O")):
                (btn_list, btn_marker) = btn_type

                for k in btn_list:
                    buttons[cls.make_btn_key(k, btn_marker)] = k

            record = {"key": key, cls.BUTTONS_KEY: buttons}
            db.polls.insert_one(record)
            poll = cls(db, record)

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

        game_key = self.buttons[button_id]

        if game_key not in self.selections:
            self.selections[game_key] = [user_key]
        else:
            if user_key in self.selections[game_key]:
                self.selections[game_key].remove(user_key)
            else:
                self.selections[game_key].append(user_key)

        self.db.polls.update_one({"key": self.key}, {"$set": {self.SELECTIONS_KEY: self.selections}})
