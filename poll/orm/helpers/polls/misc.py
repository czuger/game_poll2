from poll.misc.objects import ButtonType
from poll.misc.params_bundle import ParamsBundle
from poll.orm.poll_orm_object import PollOrmObject, PollElement


async def set_default_games(params_b: ParamsBundle) -> ParamsBundle:
    """To be called when creating a new poll"""
    for game_key in params_b.guild.poll_default_games:
        params_b.poll.poll_elements[game_key] = PollElement(object_key=game_key, object_type=ButtonType.GAME)

    await params_b.poll.save()

    return params_b


def get_players_count(poll: PollOrmObject) -> int:
    """Required to alert people about the size of the room"""
    players_set = set()

    for game in poll.poll_elements.values():
        for voter in game.votes.votes:
            players_set.add(voter)

    return len(players_set)
