from datetime import datetime
from typing import Tuple

from poll.orm.guild_orm_object import GuildOrmObject, VotesData
from poll.orm.poll_orm_object import PollOrmObject, ButtonObject, ButtonType


async def reset_votes(poll: PollOrmObject, guild: GuildOrmObject) -> Tuple[PollOrmObject, GuildOrmObject]:
    for button in poll.buttons.values():
        button: ButtonObject

        if button.object_type == ButtonType.GAME:
            if button.object_key not in guild.total_votes_data:
                guild.total_votes_data[button.object_key] = VotesData()

            guild.total_votes_data[button.object_key].total_votes_count += button.votes.votes_count
            guild.total_votes_data[button.object_key].last_vote = button.votes.last_vote

        button.votes.votes = []
        button.votes.votes_count = 0
        button.votes.last_vote = None

    poll.save()
    guild.save()

    return poll, guild


async def toggle_vote(poll: PollOrmObject, button_key: str, user_key: int) -> PollOrmObject:
    button = poll.buttons[button_key]
    current_votes = button.votes.votes

    if user_key not in current_votes:
        return await add_vote(poll, button_key, user_key)
    else:
        return await remove_vote(poll, button_key, user_key)


async def add_vote(poll: PollOrmObject, button_key: str, user_key: int) -> PollOrmObject:
    button = poll.buttons[button_key]
    current_votes = button.votes.votes

    if user_key not in current_votes:
        button.votes.votes.append(user_key)
        button.votes.votes_count += 1
        button.votes.last_vote = datetime.now()

        await poll.save()

    return poll


async def remove_vote(poll: PollOrmObject, button_key: str, user_key: int) -> PollOrmObject:
    button = poll.buttons[button_key]
    current_votes = button.votes.votes

    if user_key in current_votes:
        button.votes.votes.remove(user_key)
        button.votes.votes_count -= 1

        await poll.save()

    return poll
