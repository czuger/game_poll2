from unittest.mock import AsyncMock, MagicMock

from poll.misc.params_bundle import ParamsBundle
from poll.orm.database import DbConnector
from poll.orm.game_orm_object import check_games_at_startup
from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.helpers.polls.misc import set_default_games
from poll.orm.poll_orm_object import PollOrmObject
from poll.orm.redis import redis_connection


def build_interaction():
    user = AsyncMock(id=252627, display_name="foo", send=AsyncMock())

    discord_guild = AsyncMock(id=123456, get_member=MagicMock())
    discord_guild.get_member.return_value = user

    discord_channel = MagicMock(id=123456, guild=discord_guild)

    message = AsyncMock(edit=AsyncMock())
    message.edit.return_value = 0

    response = AsyncMock(defer=AsyncMock())
    response.defer.return_value = 0

    interaction = AsyncMock(channel=discord_channel, user=user, message=message, response=response)
    return interaction


class BotTest:

    def __init__(self):
        self.db = None
        self.guild = None
        self.poll = None
        self.params_b = None
        self.interaction = None

    async def set_up(self):
        self.db = DbConnector()
        await self.db.connect("games_database_tests")
        await self.db.clear_db()

        redis = redis_connection()

        await check_games_at_startup()

        self.guild = await GuildOrmObject.find_one(PollOrmObject.key == "123456")
        self.poll = await PollOrmObject.find_one(PollOrmObject.key == "123456")

        if not self.guild:
            self.guild = GuildOrmObject(key="123456")
            await self.guild.insert()

        if not self.poll:
            self.poll = PollOrmObject(key="123456")
            await self.poll.insert()

        self.interaction = build_interaction()

        self.params_b = ParamsBundle(poll=self.poll, guild=self.guild, redis_connection=redis,
                                     interaction=self.interaction, add_game_button_interaction=self.interaction)
        self.params_b = await set_default_games(self.params_b)

    def close(self):
        self.db.close()
        self.db = None

    async def set_admin(self, user_id: int, super_admin=False):
        await self.db.admins.update_one(
            {"user_id": user_id},  # Filter to match the document
            {"$set": {"super_admin": super_admin}},  # Update operation
            upsert=True  # Insert a new document if no matching document exists
        )

    async def set_super_admin(self, user_id: int):
        await self.set_admin(user_id, True)
