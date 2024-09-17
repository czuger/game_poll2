from discord.ext import commands

from libs.dat.database import DbConnector
from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed
from libs.poll.poll_view import PollView


class PollCog(commands.Cog, name="sondages"):
    "Commandes relatives aux sondages"

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def __show_poll(ctx: commands.Context, db: DbConnector, poll: Poll):
        """Display the poll information with an interactive view."""
        # Create a new PollView instance
        pv = PollView()

        # Initialize the view with the poll data from the database
        await pv.initialize_view(db, poll)

        # Generate the embed containing the player information
        embed = await get_players_embed(db, ctx.channel)

        # Send the message with the embed and the interactive view
        await ctx.send(embed=embed, view=pv)

    @commands.command(name="sondage")
    async def poll(self, ctx: commands.Context, db: DbConnector):
        """Affiche un sondage lié à un canal."""
        # Fetch or create the poll for the current channel
        poll = await Poll.find(db, ctx.channel, create_if_not_exist=True)

        # Display the poll using the __show_poll method
        await self.__show_poll(ctx, db, poll)

    @commands.command(name="sondage_")
    async def reset_poll(self, ctx: commands.Context, db: DbConnector):
        """Supprime et recrée les informations relatives à un sondage."""
        # Find the poll for the current channel
        poll = await Poll.find(db, ctx.channel)

        # Remove the current poll from the database
        await poll.remove_poll_from_db()

        # Create a new poll after resetting
        poll = await Poll.find(db, ctx.channel, create_if_not_exist=True)

        # Display the new poll using the __show_poll method
        await self.__show_poll(ctx, db, poll)
