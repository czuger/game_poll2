from discord.ext import commands
from discord.ext.commands import Context
from poll.libs.objects.guild import Guild

from poll.commands_response.admin import is_super_admin
from poll.misc.logging.command_logger import log_command_call
from poll.orm.database import DbConnector


class GuildsCog(commands.Cog, name="guildes"):
    """All commands related to guild management"""

    def __init__(self, bot, db: DbConnector):
        self.bot = bot
        self.db = db

    @commands.command()
    async def reset_guild(self, ctx: Context):
        """Supprime et recrée les informations relatives au serveur (super admin uniquement)"""
        log_command_call(ctx.author, ctx.channel, "reset_guild")

        if await is_super_admin(self.db, ctx, ctx.me.id):
            guild = await Guild.find_or_create_by_channel(self.db, ctx.channel)
            await guild.remove_poll_from_db()
            await Guild.find_or_create_by_channel(self.db, ctx.channel)
