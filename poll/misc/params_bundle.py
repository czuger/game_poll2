from dataclasses import dataclass
from typing import Optional

import redis
from discord import Interaction, Guild

from poll.gamebot import GameBot
from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.poll_orm_object import PollOrmObject


@dataclass
class ParamsBundle:
    # Connections
    redis_connection: Optional[redis.Redis] = None

    # Orm objects
    poll: Optional[PollOrmObject] = None
    guild: Optional[GuildOrmObject] = None

    # Discord objects
    interaction: Optional[Interaction] = None
    add_game_button_interaction: Optional[Interaction] = None
    discord_guild_object: Optional[Guild] = None
    discord_bot: GameBot = None
