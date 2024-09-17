from discord.ext import commands
from discord.ext.commands import Context

from libs.dat.database import DbConnector
from libs.dat.guild import Guild


class GuildsCog(commands.Cog, name="guildes"):
    """All commands related to guild management"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reset_guild(self, ctx: Context, db: DbConnector):
        """Supprime et recrée les informations relatives au serveur (super admin uniquement)"""
        # if await is_super_admin(db, ctx.interaction, ctx.me.id):
        guild = await Guild.find_or_create(db, ctx.channel)
        await guild.remove_poll_from_db()
        await Guild.find_or_create(db, ctx.channel)
