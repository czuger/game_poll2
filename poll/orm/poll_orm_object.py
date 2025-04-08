import copy
from dataclasses import field
from datetime import datetime
from enum import Enum, auto
from typing import Optional

import discord
from beanie import Document
from pydantic import BaseModel

from poll.orm.guild_orm_object import GuildOrmObject

default_misc = {"schedule": None, "last_schedule": datetime.now()}

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

MAX_ROWS = 5
MAX_COLS = 5


class Schedule(BaseModel):
    schedule_day: int
    schedule_hour: int

    last_schedule: Optional[datetime] = None


class Votes(BaseModel):
    votes: list = field(default_factory=lambda: [])
    votes_count: int = 0
    last_vote: Optional[datetime] = None


class ButtonType(Enum):
    """Enum representing button types: game or other."""
    GAME = auto()
    OTHER = auto()


class ButtonObject(BaseModel):
    object_key: str
    object_type: ButtonType

    votes: Votes = field(default_factory=lambda: Votes())


class PollOrmObject(Document):
    """
    PollOrmObject button object structure
    "adg_123456": {
      "game_key": adg,
      "votes": [1, 2, 3]
    }
    """
    key: str

    default_games: list = field(default_factory=lambda: [])

    # Buttons data
    buttons: dict[str, ButtonObject] = field(default_factory=lambda: {})

    # Buttons rows for display only
    buttons_rows: list = field(default_factory=lambda: [])

    schedule: Optional[Schedule] = None

    # If we need optional other buttons, use booleans. If no boolean associated, then the buttons are mandatory.
    # others: boolean
    # add: boolean

    class Settings:
        name = "polls"

    async def set_default_games(self, guild: GuildOrmObject):
        """To be called when creating a new poll"""
        self.default_games = copy.copy(guild.poll_default_games)

        await self.save()

    def get_players_count(self):
        """Required to alert people about the size of the room"""
        players_set = set()

        for game in self.games.values():
            for voter in game.votes:
                players_set.add(voter)

        return len(players_set)
