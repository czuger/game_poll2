import uuid
from enum import Enum, auto
from typing import Optional

import discord
import redis
from pydantic import BaseModel

from poll.orm.game_orm_object import get_game_short
from poll.orm.poll_orm_object import OTHER_BUTTONS
from poll.orm.redis import save_button_associated_key


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


async def build_poll_button_element(redis_connection: redis.Redis, button_type: ButtonType, key: str,
                                    row: int) -> PollButtonElement:
    button_key = _key = key + "_" + str(uuid.uuid4())

    await save_button_associated_key(redis_connection, button_key, key)

    if button_type == ButtonType.GAME:
        return PollButtonElement(key=button_key, row=row, short_str=await get_game_short(key),
                                 style=discord.ButtonStyle.grey.value)
    else:
        return PollButtonElement(
            key=button_key, row=row, short_str=OTHER_BUTTONS[key]["short"], emoji=OTHER_BUTTONS[key]["emoji"],
            style=OTHER_BUTTONS[key]["style"].value)
