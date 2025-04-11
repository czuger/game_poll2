from poll.interfaces.poll.helpers.build_poll_button_element import build_poll_button_element, PollButtonElement
from poll.misc.constants import MAX_COLS_IN_POLL, MAX_ROWS_IN_POLL, OTHER_BUTTONS
from poll.misc.params_bundle import ParamsBundle
from poll.orm.poll_orm_object import ButtonType


async def build_buttons_list(params_b: ParamsBundle) -> list[PollButtonElement]:
    """Rebuild the buttons list and build the row lists."""
    buttons = []
    row_count = 0

    for game_key in sorted(params_b.poll.poll_elements):
        button = await build_poll_button_element(params_b, ButtonType.GAME, game_key, row_count)
        buttons.append(button)

        if len(buttons) >= MAX_COLS_IN_POLL:
            row_count += 1

        if row_count >= MAX_ROWS_IN_POLL:
            break

    for other_keys in OTHER_BUTTONS.keys():
        button = await build_poll_button_element(params_b, ButtonType.OTHER, other_keys, row_count)
        buttons.append(button)

    return buttons
