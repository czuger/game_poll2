import uuid
from typing import Tuple, Optional

from poll.interfaces.add_game.add_game_to_poll.select_game_to_remove import select_game_to_remove
from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.poll_orm_object import PollOrmObject, ButtonObject, ButtonType


def make_room_for_new_game(poll: PollOrmObject, guild: GuildOrmObject) -> Tuple[PollOrmObject, GuildOrmObject]:
    game_key_to_remove = select_game_to_remove(guild)

    guild.total_votes_data[game_key_to_remove].total_votes_count += poll.games[game_key_to_remove].votes_count
    guild.total_votes_data[game_key_to_remove].last_vote += poll.games[game_key_to_remove].last_vote

    del poll.games[game_key_to_remove]

    return poll, guild


async def add_game_to_poll(poll: PollOrmObject, guild: GuildOrmObject, game_key: str) -> Tuple[
    PollOrmObject, GuildOrmObject, Optional[str]]:
    if game_key not in poll.games:
        if len(poll.games) >= 20:
            poll, guild = make_room_for_new_game(poll, guild)
            poll.rebuild_buttons()

        poll.games[game_key] = GameObject()

        button_key = _key = game_key + "_" + str(uuid.uuid4())
        poll.games_buttons[button_key] = ButtonObject(object_key=game_key, object_type=ButtonType.GAME)

        await poll.save()

    return poll, guild, None
