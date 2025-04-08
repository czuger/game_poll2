from discord import Message, Member

users_cache = {}


async def get_user_name(message: Message, user_id: int) -> str:
    global users_cache

    user = users_cache.get(user_id, None)  # noqa

    if not user:
        user = message.guild.get_member(user_id)
        user: Member
        users_cache[user_id] = user

    return user.display_name
