from dataclasses import field
from datetime import datetime
from typing import Optional

from beanie import Document
from beanie.odm.operators.update.array import AddToSet, Pull
from beanie.odm.operators.update.general import Set
from pydantic import BaseModel

default_misc = {"schedule": None, "last_schedule": datetime.now()}


class Misc(BaseModel):
    schedule: Optional[int] = None
    last_schedule: datetime = datetime.now()


class PollOrmObject(Document):
    key: str

    # Button id, game_key
    buttons: dict[str, str] = field(default_factory=lambda: {})

    misc: Misc = Misc(schedule=None, last_schedule=datetime.now())

    # Game key, user list
    votes: dict[str, list] = field(default_factory=lambda: {})

    # If we need optional other buttons, use booleans. If no boolean associated, then the buttons are mandatory.
    # others: boolean
    # add: boolean

    class Settings:
        name = "polls"

    async def add_vote(self, game_key: str, user_key: str):
        current_votes = self.votes.get(game_key, None)
        if not current_votes:
            await self.update(Set({PollOrmObject.votes[game_key]: []}))
            current_votes = []

        if user_key not in current_votes:
            await self.update(AddToSet({PollOrmObject.votes[game_key]: user_key}))

    async def remove_vote(self, game_key: str, user_key: str):
        current_votes = self.votes.get(game_key, [])
        if user_key in current_votes:
            await self.update(Pull({PollOrmObject.votes[game_key]: user_key}))
