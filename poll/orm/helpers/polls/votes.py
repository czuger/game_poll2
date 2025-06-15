from datetime import datetime
from typing import Tuple

from poll.misc.params_bundle import ParamsBundle
from poll.orm.guild_orm_object import GuildOrmObject, VotesData
from poll.orm.poll_orm_object import PollElement


async def reset_votes(params_b: ParamsBundle) -> ParamsBundle:
    for element_object in params_b.poll.poll_elements.values():
        element_object.votes.votes = []

    params_b.poll.save()

    return params_b


def __increase_guild_vote(guild: GuildOrmObject, element_key: str) -> GuildOrmObject:
    vote_element = guild.total_votes_data.get(element_key, None)

    if not vote_element:
        guild.total_votes_data[element_key] = VotesData(total_votes_count=1, last_vote=datetime.now())
    else:
        vote_element.total_votes_count += 1
        vote_element.last_vote = datetime.now()

    return guild


def __decrease_guild_vote(guild: GuildOrmObject, element_key: str) -> GuildOrmObject:
    vote_element = guild.total_votes_data.get(element_key, None)

    if not vote_element:
        raise RuntimeError(f"Can't decrease {element_key} for {guild} as element does not exist.")
    else:
        vote_element.total_votes_count -= 1

    return guild


def __get_votes(params_b: ParamsBundle, element_key: str) -> Tuple[PollElement, list]:
    """Return the """
    poll_element = params_b.poll.poll_elements[element_key]

    if not poll_element:
        raise RuntimeError(f"{element_key} not in {params_b.poll.poll_elements.keys()}")

    return poll_element, poll_element.votes.votes


async def add_vote(params_b: ParamsBundle, element_key: str, user_key: int) -> ParamsBundle:
    poll_element, current_votes = __get_votes(params_b, element_key)

    if user_key not in __get_votes(params_b, element_key):
        poll_element.votes.votes.append(user_key)
        params_b.guild = __increase_guild_vote(params_b.guild, element_key)

        await params_b.poll.save()

    return params_b


async def remove_vote(params_b: ParamsBundle, element_key: str, user_key: int) -> ParamsBundle:
    poll_element, current_votes = __get_votes(params_b, element_key)

    if user_key in current_votes:
        poll_element.votes.votes.remove(user_key)
        params_b.guild = __decrease_guild_vote(params_b.guild, element_key)

        await params_b.poll.save()

    return params_b


async def toggle_vote(params_b: ParamsBundle, element_key: str, user_key: int) -> ParamsBundle:
    _, current_votes = __get_votes(params_b, element_key)

    if user_key not in current_votes:
        return await add_vote(params_b, element_key, user_key)
    else:
        return await remove_vote(params_b, element_key, user_key)
