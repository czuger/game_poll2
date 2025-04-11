from datetime import datetime

from poll.misc.params_bundle import ParamsBundle
from poll.orm.guild_orm_object import VotesData
from poll.orm.poll_orm_object import PollOrmObject, ButtonType


async def reset_votes(params_b: ParamsBundle) -> ParamsBundle:
    for element_object in params_b.poll.poll_elements.values():

        if element_object.object_type == ButtonType.GAME:
            if element_object.object_key not in params_b.guild.total_votes_data:
                params_b.guild.total_votes_data[element_object.object_key] = VotesData()

            params_b.guild.total_votes_data[
                element_object.object_key].total_votes_count += element_object.votes.votes_count
            params_b.guild.total_votes_data[element_object.object_key].last_vote = element_object.votes.last_vote

        element_object.votes.votes = []
        element_object.votes.votes_count = 0
        element_object.votes.last_vote = None

    params_b.poll.save()
    params_b.guild.save()

    return params_b


async def toggle_vote(poll: PollOrmObject, element_key: str, user_key: int) -> PollOrmObject:
    element = poll.poll_elements[element_key]
    current_votes = element.votes.votes

    if user_key not in current_votes:
        return await add_vote(poll, element_key, user_key)
    else:
        return await remove_vote(poll, element_key, user_key)


async def add_vote(poll: PollOrmObject, element_key: str, user_key: int) -> PollOrmObject:
    element = poll.poll_elements[element_key]
    current_votes = element.votes.votes

    if user_key not in current_votes:
        element.votes.votes.append(user_key)
        element.votes.votes_count += 1
        element.votes.last_vote = datetime.now()

        await poll.save()

    return poll


async def remove_vote(poll: PollOrmObject, element_key: str, user_key: int) -> PollOrmObject:
    element = poll.poll_elements[element_key]
    current_votes = element.votes.votes

    if user_key in current_votes:
        element.votes.votes.remove(user_key)
        element.votes.votes_count -= 1

        await poll.save()

    return poll
