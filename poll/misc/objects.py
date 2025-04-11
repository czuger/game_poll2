from enum import Enum, auto
from typing import Optional

import discord
from pydantic import BaseModel


class ButtonType(Enum):
    """Enum representing button types: game or other."""
    GAME = auto()
    OTHER = auto()


class PollButtonElement(BaseModel):
    key: str
    row: int
    short_str: str
    emoji: Optional[str] = None
    style: Optional[int] = discord.ButtonStyle.grey.value
