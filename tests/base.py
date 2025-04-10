from poll.libs.objects.database import DbConnector
from poll.orm.game_orm_object import check_games_at_startup
from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.helpers.polls.misc import set_default_games
from poll.orm.helpers.polls.rebuild_buttons import rebuild_buttons
from poll.orm.poll_orm_object import PollOrmObject


class BotTest:

    def __init__(self):
        self.db = None
        self.guild = None
        self.poll = None

    async def set_up(self):
        self.db = DbConnector()
        await self.db.connect("games_database_tests")
        await self.db.clear_db()

        await check_games_at_startup()

        self.guild = await GuildOrmObject.find_one(PollOrmObject.key == "123456")
        self.poll = await PollOrmObject.find_one(PollOrmObject.key == "123456")

        if not self.guild:
            self.guild = GuildOrmObject(key="123456")
            await self.guild.insert()

        if not self.poll:
            self.poll = PollOrmObject(key="123456")
            await self.poll.insert()

        self.poll = await set_default_games(self.poll, self.guild)
        self.poll = await rebuild_buttons(self.poll)

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
