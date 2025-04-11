from poll.discord.users import get_user_name
from poll.misc.constants import OTHER_BUTTONS
from poll.misc.objects import ButtonType
from poll.misc.params_bundle import ParamsBundle
from poll.orm.game_orm_object import get_game_long
from poll.orm.poll_orm_object import PollElement


async def get_poll_embedded_lines(params_b: ParamsBundle) -> list[str]:
    """Show poll lines as to be shown in the poll"""
    other_results = []
    game_results = []

    for poll_element in params_b.poll.poll_elements.values():
        poll_element: PollElement

        if poll_element.votes.votes_count > 0:
            if poll_element.object_type == ButtonType.GAME:
                object_name = await get_game_long(poll_element.object_key)
            else:
                object_name = OTHER_BUTTONS[poll_element.object_key]["long"]

            users_names = [await get_user_name(params_b.discord_guild_object, user_key) for user_key in
                           poll_element.votes.votes]
            users_names.sort()
            users_list = ", ".join(users_names)

            if poll_element.object_type == ButtonType.OTHER:
                other_results.append(f"**{object_name}** : {users_list}")
            else:
                game_results.append(f"**{object_name}** : {users_list}")

    return other_results + game_results
