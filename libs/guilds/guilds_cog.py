from discord.ext import commands
from discord.ext.commands import Context

from libs.admin import is_super_admin
from libs.dat.database import DbConnector
from libs.dat.guild import Guild


class GuildsCog(commands.Cog, name="guildes"):
    """All commands related to guild management"""

    def __init__(self, bot, db: DbConnector):
        self.bot = bot
        self.db = db

    @commands.command()
    async def reset_guild(self, ctx: Context):
        """Supprime et recrée les informations relatives au serveur (super admin uniquement)"""
        if await is_super_admin(self.db, ctx.interaction, ctx.me.id):
            guild = await Guild.find_or_create(self.db, ctx.channel)
            await guild.remove_poll_from_db()
            await Guild.find_or_create(self.db, ctx.channel)
