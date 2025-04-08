import copy
import uuid

from poll.orm.poll_orm_object import PollOrmObject, ButtonObject, ButtonType, MAX_COLS, MAX_ROWS, OTHER_BUTTONS


async def rebuild_buttons(poll: PollOrmObject) -> PollOrmObject:
    """Rebuild the buttons list and build the row lists."""
    poll.buttons = {}

    current_row = []
    row_count = 0
    for game_key in sorted(poll.default_games):
        button_key = _key = game_key + "_" + str(uuid.uuid4())
        poll.buttons[button_key] = ButtonObject(object_key=game_key, object_type=ButtonType.GAME)

        current_row.append(button_key)
        if len(current_row) >= MAX_COLS:
            row_count += 1
            poll.buttons_rows.append(copy.copy(current_row))
            current_row = []

        if row_count >= MAX_ROWS:
            break

    if row_count < MAX_COLS and current_row:
        poll.buttons_rows.append(copy.copy(current_row))

    current_row = []
    for other_keys in OTHER_BUTTONS.keys():
        button_key = _key = other_keys + "_" + str(uuid.uuid4())
        poll.buttons[button_key] = ButtonObject(object_key=other_keys, object_type=ButtonType.OTHER)
        current_row.append(button_key)

    poll.buttons_rows.append(current_row)
    await poll.save()

    return poll
