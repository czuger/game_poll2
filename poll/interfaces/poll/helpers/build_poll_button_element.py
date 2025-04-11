import uuid

import discord

from poll.misc.constants import OTHER_BUTTONS
from poll.misc.objects import ButtonType, PollButtonElement
from poll.misc.params_bundle import ParamsBundle
from poll.orm.game_orm_object import get_game_short
from poll.orm.redis import save_button_associated_key


async def build_poll_button_element(params_b: ParamsBundle, button_type: ButtonType, key: str,
                                    row: int) -> PollButtonElement:
    button_key = _key = key + "_" + str(uuid.uuid4())

    await save_button_associated_key(params_b.redis_connection, button_key, key)

    if button_type == ButtonType.GAME:
        return PollButtonElement(key=button_key, row=row, short_str=await get_game_short(key),
                                 style=discord.ButtonStyle.grey.value)
    else:
        return PollButtonElement(
            key=button_key, row=row, short_str=OTHER_BUTTONS[key]["short"], emoji=OTHER_BUTTONS[key]["emoji"],
            style=OTHER_BUTTONS[key]["style"].value)
