import redis

from poll.orm.helpers.polls.build_poll_button_element import build_poll_button_element
from poll.orm.poll_orm_object import PollOrmObject, ButtonObject, ButtonType, MAX_COLS, MAX_ROWS, OTHER_BUTTONS


# button = RespondToAddGameButton(
#     db, poll, other["short"], key, row, emoji=other["emoji"], style=self.get_style_from_poll(other))


async def rebuild_buttons(redis_connection: redis.Redis, poll: PollOrmObject) -> PollOrmObject:
    """Rebuild the buttons list and build the row lists."""
    poll.buttons = {}

    poll.buttons_for_view = []
    row_count = 0
    for game_key in sorted(poll.selected_games):
        button = await build_poll_button_element(redis_connection, ButtonType.GAME, game_key, row_count)
        poll.buttons[button.key] = ButtonObject(object_key=game_key, object_type=ButtonType.GAME)
        poll.buttons_for_view.append(button)

        if len(poll.buttons_for_view) >= MAX_COLS:
            row_count += 1

        if row_count >= MAX_ROWS:
            break

    for other_keys in OTHER_BUTTONS.keys():
        button = await build_poll_button_element(redis_connection, ButtonType.OTHER, other_keys, row_count)
        poll.buttons[button.key] = ButtonObject(object_key=other_keys, object_type=ButtonType.OTHER)
        poll.buttons_for_view.append(button)

    await poll.save()

    return poll
