from dataclasses import field
from datetime import datetime
from typing import Optional

import discord
from beanie import Document
from pydantic import BaseModel

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


class Schedule(BaseModel):
    schedule: Optional[int] = None
    last_schedule: datetime = datetime.now()


class GameObject(BaseModel):
    votes: list = field(default_factory=lambda: [])
    votes_count: int = 0
    last_vote: Optional[datetime] = None


class PollOrmObject(Document):
    """
    PollOrmObject button object structure
    "adg_123456": {
      "game_key": adg,
      "votes": [1, 2, 3]
    }
    """
    key: str

    # Game key, game object
    games: dict[str, GameObject] = field(default_factory=lambda: {})

    # Button id, game_key
    games_buttons: dict[str, str] = field(default_factory=lambda: {})

    schedule: Schedule

    # If we need optional other buttons, use booleans. If no boolean associated, then the buttons are mandatory.
    # others: boolean
    # add: boolean

    class Settings:
        name = "polls"

    def get_players_count(self):
        """Required to alert people about the size of the room"""
        players_set = set()

        for game in self.games.values():
            for voter in game.votes:
                players_set.add(voter)

        return len(players_set)

    async def add_vote(self, button_key: str, user_key: str):
        game_key = self.games_buttons[button_key]
        current_votes = self.games[game_key].votes

        if user_key not in current_votes:
            self.games[game_key].votes.append(user_key)
            self.games[game_key].votes_count += 1
            self.games[game_key].last_vote = datetime.now()

            await self.save()

    async def remove_vote(self, button_key: str, user_key: str):
        game_key = self.games_buttons[button_key]
        current_votes = self.games[game_key].votes

        if user_key in current_votes:
            self.games[game_key].votes.remove(user_key)
            self.games[game_key].votes_count -= 1

            await self.save()
