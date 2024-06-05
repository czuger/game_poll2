import discord
from discord.ext import commands

from libs.poll.poll import Poll
from libs.poll.poll_view import PollView


class GameBot(commands.Bot):
    """
    The main GameBot class.
    """
    def __init__(self, db):
        """
        Initialize the GameBot instance.

        Parameters
        ----------
        db : Database
            Database instance to store and manage game data.

        Returns
        -------
        None

        """
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True  # This is a privileged intent, must be enabled in the portal too.
        intents.message_content = True  # This enables the "Message Content" intent

        super().__init__(command_prefix="g2!", intents=intents)

        self.db = db

    async def setup_hook(self) -> None:
        """
        Setup hook for the GameBot.

        This method sets up a hook for the GameBot to refresh messages related to polls.
        """
        async def message_refresh_function(poll_key):
            refreshing_poll = await Poll.find(self.db, poll_key)
            pv = PollView()
            await pv.initialize_view(self.db, refreshing_poll)

        for to_refresh_poll in self.db.poll_instances.find():
            await message_refresh_function(to_refresh_poll["key"])

    async def on_ready(self):
        """
        Event handler for when the bot is ready.

        This method is called when the bot is successfully logged in and ready to start receiving events.
        """
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
