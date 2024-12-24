import logging

import discord
from discord.ext import commands
from discord.ext import tasks

from poll.libs.cogs.admin_cog import AdminManagementCog
from poll.libs.cogs.games_cog import GamesCog
from poll.libs.misc.bot.schedule_poll import check_schedules_for_polls
from poll.libs.objects.poll import Poll
from poll.libs.cogs.poll_cog import PollCog
from poll.libs.poll.poll_view import PollView

logger = logging.getLogger(__name__)


@tasks.loop(hours=1)
async def check_schedules(db, bot):
    await check_schedules_for_polls(db, bot)


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
        self.gpt_key = None

    async def setup_hook(self) -> None:
        """
        Setup hook for the GameBot.

        This method sets up a hook for the GameBot to refresh messages related to polls.
        """

        async def message_refresh_function(poll_dict):
            refreshing_poll = await Poll.get_bot_at_restart(self, self.db, poll_dict)
            pv = PollView()
            initialized_view = await pv.initialize_view(self.db, refreshing_poll)

            self.add_view(initialized_view)
            logger.debug(initialized_view, initialized_view.id)

        # print(self.db.poll_instances)

        cursor = self.db.poll_instances.find()
        polls = await cursor.to_list(length=None)

        for to_refresh_poll in polls:
            # print(to_refresh_poll)
            logger.debug("Refreshing poll", to_refresh_poll)
            await message_refresh_function(to_refresh_poll)

        check_schedules.start(self.db, self)

        await self.add_cog(PollCog(self, self.db))
        # await self.add_cog(GuildsCog(self, self.db))
        await self.add_cog(GamesCog(self, self.db))
        await self.add_cog(AdminManagementCog(self, self.db))

    async def on_ready(self):
        """
        Event handler for when the bot is ready.

        This method is called when the bot is successfully logged in and ready to start receiving events.
        """
        logger.debug(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.debug('------')
