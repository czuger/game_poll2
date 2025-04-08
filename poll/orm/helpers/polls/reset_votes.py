from typing import Tuple

from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.poll_orm_object import PollOrmObject, GameObject


async def reset_votes(poll: PollOrmObject, guild: GuildOrmObject) -> Tuple[PollOrmObject, GuildOrmObject]:
    for game_key, game in poll.games:
        game: GameObject

        guild.total_votes_data[game_key].total_votes_count += game.votes_count
        guild.total_votes_data[game_key].last_vote += game.last_vote

        game.votes = []
        game.votes_count = 0
        game.last_vote = None

    poll.save()
    guild.save()

    return poll, guild
