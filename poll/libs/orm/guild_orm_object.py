from typing import List

from beanie import Document, Link

from poll.libs.orm.game_orm_object import GameOrmObject


class GuildOrmObject(Document):
    key: str

    # The current games available on the guild
    games: List[Link[GameOrmObject]]

    class Settings:
        name = "guilds"
