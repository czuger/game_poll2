import logging

from discord.ext import commands

from poll.libs.objects.admin import is_admin
from poll.libs.objects.admin import is_super_admin
from poll.libs.objects.database import DbConnector
from poll.libs.misc.logging.command_logger import log_command_call
from poll.libs.misc.constants import DEFAULT_DELETE_AFTER
from poll.libs.misc.bot.schedule_poll import schedule_poll
from poll.libs.misc.logging.set_logging import POLLS_LOG_NAME
from poll.libs.objects.poll import Poll
from poll.libs.objects.poll import PollNotFound
from poll.libs.poll.poll_embedding import get_players_embed
from poll.libs.poll.poll_view import PollView

poll_logger = logging.getLogger(POLLS_LOG_NAME)


class PollCog(commands.Cog, name="sondages"):
    """Commandes relatives aux sondages"""

    def __init__(self, bot, db: DbConnector):
        self.bot = bot
        self.db = db

    async def __show_poll(self, ctx: commands.Context, poll: Poll):
        """Display the poll information with an interactive view."""
        # Create a new PollView instance
        pv = PollView()

        # Initialize the view with the poll data from the database
        await pv.initialize_view(self.db, poll)

        # Generate the embed containing the player information
        embed = await get_players_embed(self.db, ctx.channel)

        # Send the message with the embed and the interactive view
        await ctx.send(embed=embed, view=pv)

    @commands.command(name="sondage")
    async def poll(self, ctx: commands.Context):
        """Affiche un sondage lié à un canal."""
        # Fetch or create the poll for the current channel
        log_command_call(ctx.author, ctx.channel, "jeux")

        poll = await Poll.find(self.db, ctx.channel, create_if_not_exist=True)

        # Display the poll using the __show_poll method
        await self.__show_poll(ctx, poll)

    @commands.command(name="reinit")
    async def reset_poll(self, ctx: commands.Context):
        """Supprime et recrée les informations relatives à un sondage (super admin)"""
        log_command_call(ctx.author, ctx.channel, "reinit")

        try:
            if await is_super_admin(self.db, ctx, ctx.author.id):
                # Find the poll for the current channel
                poll = await Poll.find(self.db, ctx.channel)

                # Remove the current poll from the database
                await poll.remove_poll_from_db()

                # Create a new poll after resetting
                poll = await Poll.find(self.db, ctx.channel, create_if_not_exist=True)

                # Display the new poll using the __show_poll method
                await self.__show_poll(ctx, poll)
        except PollNotFound:
            await ctx.send(content="Le sondage n'existe pas.", ephemeral=True, delete_after=DEFAULT_DELETE_AFTER)

    @commands.command(name="supp_votes")
    async def reset_votes(self, ctx: commands.Context):
        """Supprime les votes pour un sondage donné (admin)"""
        log_command_call(ctx.author, ctx.channel, "votes")

        if await is_admin(self.db, ctx, ctx.author.id):
            # Find the poll for the current channel
            poll = await Poll.find(self.db, ctx.channel)

            # Reset votes
            await poll.reset_votes()

            # Display the new poll using the __show_poll method
            await self.__show_poll(ctx, poll)

    @commands.command(name="planif_jeux")
    async def schedule_polls(self, ctx: commands.Context, day: int):
        if await is_admin(self.db, ctx, ctx.author.id):
            await schedule_poll(self.db, ctx, day)

    # TODO : we need a command to list poll

    # TODO : we need a command to remove a poll
