from dataclasses import field
from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import BaseModel

from poll.interfaces.poll.helpers.build_poll_button_element import ButtonType

default_misc = {"schedule": None, "last_schedule": datetime.now()}


class Schedule(BaseModel):
    schedule_day: int
    schedule_hour: int

    last_schedule: Optional[datetime] = None


class Votes(BaseModel):
    votes: list = field(default_factory=lambda: [])
    votes_count: int = 0
    last_vote: Optional[datetime] = None


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
    key: str

    poll_elements: dict[str, PollElement] = field(default_factory=lambda: {})

    schedule: Optional[Schedule] = None

    # If we need optional other buttons, use booleans. If no boolean associated, then the buttons are mandatory.
    # others: boolean
    # add: boolean

    class Settings:
        name = "polls"
