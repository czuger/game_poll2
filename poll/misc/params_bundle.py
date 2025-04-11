from dataclasses import dataclass
from typing import Optional

import redis
from discord import Interaction, Guild


@dataclass
class ParamsBundle:
    # Connections
    redis_connection: Optional[redis.Redis] = None

    # Orm objects
    poll: Optional["PollOrmObject"] = None  # noqa
    guild: Optional["GuildOrmObject"] = None  # noqa

    # Discord objects
    interaction: Optional[Interaction] = None
    add_game_button_interaction: Optional[Interaction] = None
    discord_guild_object: Optional[Guild] = None
