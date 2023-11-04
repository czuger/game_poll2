import uuid

import discord

from libs.guild import Guild


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

    def __init__(self, polls, record):
        self.key = record["key"]
        self.games = record["games"]
        self.others = record["others"]

        self.polls = polls

    @classmethod
    async def find_or_create(cls, database, channel):
        key = str(channel.id)

        guild = await Guild.find_or_create(database, channel)
        polls = database["poll_instances"]

        query = {"key": key}
        existing_record = polls.find_one(query)

        if not existing_record:
            games = {}
            for _, v in guild.games.items():
                games[str(uuid.uuid4())] = v

            others = {}
            for _, v in cls.OTHER_BUTTONS.items():
                others[str(uuid.uuid4())] = v

            existing_record = {
                "key": key,
                "games": games,
                "others": others
            }

            polls.insert_one(existing_record)

        return cls(polls, existing_record)

    @classmethod
    async def find(cls, database, poll_key):
        polls = database["poll_instances"]

        query = {"key": poll_key}
        existing_record = polls.find_one(query)

        if not existing_record:
            raise RuntimeError(f"No poll for {poll_key}")

        return cls(polls, existing_record)

    def get_poll_db_object(self):
        poll = self.polls.find_one({"key": self.key})
        return poll

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

        self.polls.update_one({"key": self.key}, {"$set": {self.SELECTIONS_KEY: selections}})
