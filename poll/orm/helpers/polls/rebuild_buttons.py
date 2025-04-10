import uuid
from typing import Optional

import discord
from pydantic import BaseModel

from poll.orm.game_orm_object import get_game_short
from poll.orm.poll_orm_object import PollOrmObject, ButtonObject, ButtonType, MAX_COLS, MAX_ROWS, OTHER_BUTTONS


# button = RespondToAddGameButton(
#     db, poll, other["short"], key, row, emoji=other["emoji"], style=self.get_style_from_poll(other))


class PollButtonElement(BaseModel):
    key: str
    row: int
    short_str: str
    emoji: Optional[str] = None
    style: Optional[int] = discord.ButtonStyle.grey.value


async def build_poll_button_element(button_type: ButtonType, key: str, row: int) -> PollButtonElement:
    button_key = _key = key + "_" + str(uuid.uuid4())
    if button_type == ButtonType.GAME:
        return PollButtonElement(key=button_key, row=row, short_str=await get_game_short(key),
                                 style=discord.ButtonStyle.grey.value)
    else:
        return PollButtonElement(
            key=button_key, row=row, short_str=OTHER_BUTTONS[key]["short"], emoji=OTHER_BUTTONS[key]["emoji"],
            style=OTHER_BUTTONS[key]["style"].value)


async def rebuild_buttons(poll: PollOrmObject) -> PollOrmObject:
    """Rebuild the buttons list and build the row lists."""
    poll.buttons = {}

    poll.buttons_for_view = []
    row_count = 0
    for game_key in sorted(poll.selected_games):
        button = await build_poll_button_element(ButtonType.GAME, game_key, row_count)
        poll.buttons[button.key] = ButtonObject(object_key=game_key, object_type=ButtonType.GAME)
        poll.buttons_for_view.append(button)

        if len(poll.buttons_for_view) >= MAX_COLS:
            row_count += 1

        if row_count >= MAX_ROWS:
            break

    for other_keys in OTHER_BUTTONS.keys():
        button = await build_poll_button_element(ButtonType.OTHER, other_keys, row_count)
        poll.buttons[button.key] = ButtonObject(object_key=other_keys, object_type=ButtonType.OTHER)
        poll.buttons_for_view.append(button)

    await poll.save()

    return poll
