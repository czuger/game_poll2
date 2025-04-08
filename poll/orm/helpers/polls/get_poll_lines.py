from discord import Message

from poll.discord.users import get_user_name
from poll.orm.game_orm_object import get_game_long
from poll.orm.poll_orm_object import PollOrmObject, ButtonObject, ButtonType, OTHER_BUTTONS


async def get_poll_lines(message: Message, poll: PollOrmObject) -> list[str]:
    """Show poll lines as to be shown in the poll"""
    result = []
    for button in poll.buttons.values():
        button: ButtonObject

        if button.votes.votes_count > 0:
            if button.object_type == ButtonType.GAME:
                object_name = await get_game_long(button.object_key)
            else:
                object_name = OTHER_BUTTONS[button.object_key]["long"]

            users_names = [await get_user_name(message, user_key) for user_key in button.votes.votes]
            users_names.sort()
            users_list = ", ".join(users_names)

            result.append(f"{object_name} : {users_list}")

    return result
