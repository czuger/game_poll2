from discord import Member, Guild

users_cache = {}


async def get_user_name(guild: Guild, user_id: int) -> str:
    global users_cache

    user = users_cache.get(user_id, None)  # noqa

    if not user:
        user = guild.get_member(user_id)
        user: Member
        users_cache[user_id] = user

    return user.display_name
