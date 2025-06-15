from poll.orm.guild_orm_object import GuildOrmObject, GuildNotFound

guild_cache = {}


async def get_guild(guild_key: int, refresh=False) -> GuildOrmObject:
    """
    Retrieves a guild from the cache or database by its key.

    This function checks if the guild exists in the cache. If the refresh parameter
    is True and the guild exists in the cache, the cached entry will be removed.
    If the guild is not in the cache (or was just removed), it attempts to retrieve
    it from the database and adds it to the cache. If the guild doesn't exist in the
    database, a GuildNotFound exception is raised.

    Args:
        guild_key: The unique identifier for the guild.
        refresh: If True and the guild exists in the cache, forces a refresh of
                 the cached guild data from the database. Defaults to False.

    Returns:
        GuildOrmObject: The requested guild object.

    Raises:
        GuildNotFound: If the guild doesn't exist in the database.
    """
    global guild_cache

    if refresh and guild_cache[guild_key]:
        del guild_cache[guild_key]

    if guild_key not in guild_cache:
        guild = await GuildOrmObject.find_one(GuildOrmObject.key == guild_key)
        if not guild:
            raise GuildNotFound()
        guild_cache[guild_key] = guild

    return guild_cache[guild_key]


async def find_or_create_guild(guild_key: int) -> GuildOrmObject:
    """
    Retrieves an existing guild or creates a new one if it doesn't exist.

    Args:
        guild_key: The unique identifier for the guild.

    Returns:
        GuildOrmObject: The retrieved or newly created guild object.
    """
    try:
        guild = await get_guild(guild_key)
    except GuildNotFound:
        guild = GuildOrmObject(key=guild_key)
        guild.save()

    return guild
