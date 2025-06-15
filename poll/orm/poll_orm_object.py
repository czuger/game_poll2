from dataclasses import field
from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import BaseModel

from poll.misc.objects import ButtonType

default_misc = {"schedule": None, "last_schedule": datetime.now()}


class Schedule(BaseModel):
    schedule_day: int
    schedule_hour: int

    last_schedule: Optional[datetime] = None


class Votes(BaseModel):
    votes: list = field(default_factory=lambda: [])
    # To be removed once translation to Guild is done.
    # votes_count: int = 0
    # last_vote: Optional[datetime] = None


class PollElement(BaseModel):
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
    key: int

    # Contain the button key <key_guid>, PollElement
    poll_elements: dict[str, PollElement] = field(default_factory=lambda: {})

    schedule: Optional[Schedule] = None

    # If we need optional other buttons, use booleans. If no boolean associated, then the buttons are mandatory.
    # others: boolean
    # add: boolean

    class Settings:
        name = "polls"
