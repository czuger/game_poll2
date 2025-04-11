import json
from dataclasses import field
from datetime import datetime

from beanie import Document, Indexed
from pydantic import BaseModel

import poll.orm.game_orm_object as game_module

guild_cache = {}


async def get_pre_loaded_games(cls):
    """
    Asynchronously retrieves the keys of default games from the database.

    Parameters
    ----------

    Returns
    -------
    list
        A dict of miniatures, board and default games.
    """
    root_directory = find_project_root()

    with open(root_directory / "games" / "games.json") as f:
        result = json.load(f)
        return result["games"], result["poll_default"]


class VotesData(BaseModel):
    total_votes_count: int = 0
    last_vote: datetime = None


class GuildOrmObject(Document):
    key: Indexed(str, unique=True)

    # The current games available on the guild
    games: list = field(default_factory=lambda: game_module.default_games)

    # The games that will be added when a new poll is created
    poll_default_games: list = field(default_factory=lambda: game_module.default_games)

    # The votes count (game_key, votes)
    total_votes_data: dict[str, VotesData] = field(default_factory=lambda: {})

    class Settings:
        name = "guilds"


async def get_guild(guild_key: int) -> GuildOrmObject:
    global guild_cache

    if guild_key not in guild_cache:
        guild = await GuildOrmObject.find_one(GuildOrmObject.key == guild_key)
        if not guild:
            guild = GuildOrmObject(key=guild_key)
        guild_cache[guild_key] = guild

    return guild_cache[guild_key]
