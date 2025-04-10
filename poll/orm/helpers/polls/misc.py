import copy

from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.poll_orm_object import PollOrmObject


async def set_default_games(poll: PollOrmObject, guild: GuildOrmObject) -> PollOrmObject:
    """To be called when creating a new poll"""
    poll.selected_games = copy.copy(guild.poll_default_games)

    await poll.save()

    return poll


def get_players_count(poll: PollOrmObject) -> int:
    """Required to alert people about the size of the room"""
    players_set = set()

    for game in poll.buttons.values():
        for voter in game.votes.votes:
            players_set.add(voter)

    return len(players_set)
