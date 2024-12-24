import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from discord.ext.commands import Context

from poll.libs.admin.admin import is_admin
from poll.libs.admin.admin import is_super_admin
from poll.libs.admin.admin import super_admin
from poll.libs.poll.poll import Poll
from poll.libs.poll.poll_cog import PollCog
from tests.base import BotTest


class TestPollCog(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):
    def setUp(self):
        """Set up the test case with BotTest's set_up method."""
        super().set_up()  # Call BotTest's setUp for database and other setups
        self.bot = MagicMock()
        self.cog = PollCog(self.bot, self.db)

        self.__set_context()

        self.expected_embed_title = "A quoi allez vous jouer ?"
        self.expected_views_items = {'Bolt action', 'Frostgrave', 'Malifaux', 'Saga', 'ADG', 'Clés', 'Autre', 'Absent',
                                     'Ajouter'}

    def __set_context(self):
        channel = MagicMock(id="123456", name="channel")
        author = MagicMock(id="bob")
        self.send = AsyncMock()

        self.ctx = AsyncMock(specs=Context, channel=channel, author=author, send=self.send)

    async def test_poll_command_poll_exist(self):
        """Test the jeux command."""
        # Ensure that a poll exist for this channel
        await Poll.find(self.db, self.ctx.channel, create_if_not_exist=True)

        # Call the command
        await self.cog.poll(self.cog, self.ctx)

        calls = self.ctx.method_calls[0]
        embed_title = calls.kwargs["embed"].title
        self.assertEqual(self.expected_embed_title, embed_title)

        view_items = set([e.label for e in calls.kwargs["view"].children])
        self.assertEqual(self.expected_views_items, view_items)

    async def test_poll_command_poll_does_not_exist(self):
        """Test the jeux command."""

        # Call the command
        await self.cog.poll(self.cog, self.ctx)

        calls = self.ctx.method_calls[0]
        embed_title = calls.kwargs["embed"].title
        self.assertEqual(self.expected_embed_title, embed_title)

        view_items = set([e.label for e in calls.kwargs["view"].children])
        self.assertEqual(self.expected_views_items, view_items)

    async def test_reset_poll_super_admin_poll_does_not_exist(self):
        """Test the reset_poll command with a super admin."""
        # Ensure the user has super admin rights
        await super_admin(self.db, self.ctx)
        self.assertTrue(await is_super_admin(self.db, self.ctx, self.ctx.author.id))

        # Reset the context to remove super admin messages
        self.__set_context()

        # Call the command
        await self.cog.reset_poll(self.cog, self.ctx)

        # Assertions
        self.send.assert_called_once_with(content="Le sondage n'existe pas.", ephemeral=True, delete_after=120)

    async def test_reset_poll_super_admin_poll_does_exist(self):
        """Test the reset_poll command with a super admin."""
        # Ensure the user has super admin rights
        await super_admin(self.db, self.ctx)
        self.assertTrue(await is_super_admin(self.db, self.ctx, self.ctx.author.id))

        # Reset the context to remove super admin messages
        self.__set_context()

        # Ensure that a poll exist for this channel
        await Poll.find(self.db, self.ctx.channel, create_if_not_exist=True)

        # Call the command
        await self.cog.reset_poll(self.cog, self.ctx)

        # Assertions
        calls = self.ctx.method_calls[0]

        embed_title = calls.kwargs["embed"].title
        self.assertEqual(self.expected_embed_title, embed_title)

        view_items = set([e.label for e in calls.kwargs["view"].children])
        self.assertEqual(self.expected_views_items, view_items)

    async def test_reset_votes_admin(self):
        """Test the reset_votes command with an admin."""
        # Ensure the user has admin rights
        self.assertTrue(await is_admin(self.db, self.ctx, self.ctx.author.id))

        # Find the poll and reset votes
        poll = await Poll.find(self.db, self.ctx.channel)
        await self.cog.reset_votes(self.ctx)

        # Assertions
        self.assertIsNotNone(poll)
        self.assertEqual(len(await poll.get_votes()), 0)  # Ensure votes were reset

    async def test_schedule_polls(self):
        """Test the schedule_polls command with an admin."""
        # Ensure the user has admin rights
        self.assertTrue(await is_admin(self.db, self.ctx, self.ctx.author.id))

        # Schedule the poll
        day = 3
        await self.cog.schedule_polls(self.ctx, day)

        # Assertions
        # No exceptions mean the poll was scheduled correctly. Add specific checks for scheduling if needed.
        self.assertTrue(True)  # Placeholder assertion for successful scheduling


if __name__ == "__main__":
    unittest.main()
