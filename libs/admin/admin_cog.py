import logging

from discord.ext import commands

from libs.admin.admin import grant, \
    upgrade, revoke, downgrade
from libs.dat.database import DbConnector
from libs.misc.set_logging import ADMINS_LOG_NAME

DELETE_TIME = 15
logger = logging.getLogger(ADMINS_LOG_NAME)


class AdminManagementCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db: DbConnector):
        self.bot = bot
        self.db = db

    @commands.command(name="grant", description="Grant admin rights to a user")
    async def grant(self, ctx: commands.Context, user_id: int):
        await grant(self.db, ctx, user_id)

    @commands.command(name="upgrade", description="Upgrade a user to super admin")
    async def upgrade(self, ctx: commands.Context, user_id: int):
        await upgrade(self.db, ctx, user_id)

    @commands.command(name="downgrade", description="Downgrade a user from super admin to regular admin")
    async def downgrade(self, ctx: commands.Context, user_id: int):
        await downgrade(self.db, ctx, user_id)

    @commands.command(name="revoke", description="Revoke admin rights from a user")
    async def revoke(self, ctx: commands.Context, user_id: int):
        await revoke(self.db, ctx, user_id)

    @commands.command(name="super_admin", description="Create a super admin if none exists")
    async def super_admin(self, ctx: commands.Context):
        await super_admin(self.db, ctx)
