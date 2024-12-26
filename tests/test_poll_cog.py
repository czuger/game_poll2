import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from discord import TextChannel, User
from discord.ext.commands import Context, Author

from poll.libs.cogs.poll_cog import PollCog
from poll.libs.misc.constants import KEY
from poll.libs.objects.admin import is_super_admin, is_admin
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll
from poll.libs.objects.voters_engine import VotersEngine, ElementNotInVotesDict
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
        channel = MagicMock(specs=TextChannel, id="123456", name="channel")
        author = MagicMock(specs=Author, id="bob")
        self.user = MagicMock(specs=User, id="alice")
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
        await self.set_super_admin(self.ctx.author.id)
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
        await self.set_super_admin(self.ctx.author.id)
        self.assertTrue(await is_super_admin(self.db, self.ctx, self.ctx.author.id))

        # Reset the context to remove super admin messages
        self.__set_context()

        # Ensure that a poll exist for this channel
        await Guild.find_or_create_by_channel(self.db, self.ctx.channel)
        poll = await Poll.find(self.db, self.ctx.channel, create_if_not_exist=True)

        current_games_set = poll.get_games_keys_set()
        self.assertNotIn("congo", current_games_set)

        await poll.add_game("congo")
        await poll.refresh()
        current_games_set = poll.get_games_keys_set()
        self.assertIn("congo", current_games_set)

        # Call the command
        await self.cog.reset_poll(self.cog, self.ctx)

        await poll.refresh()

        current_games_set = poll.get_games_keys_set()
        self.assertNotIn("congo", current_games_set)

    async def test_reset_votes_admin(self):
        """Test the reset_votes command with an admin."""
        # Ensure the user has admin rights
        await self.set_admin(self.ctx.author.id)
        self.assertTrue(await is_admin(self.db, self.ctx, self.ctx.author.id))

        # Find the poll and reset votes
        poll = await Poll.find(self.db, self.ctx.channel, create_if_not_exist=True)

        button_id = poll.get_games_button_ids_list()[0]
        element_key = poll.button_id_to_element_key(button_id)

        ve = VotersEngine(poll)
        await ve.toggle_vote(self.user, button_id)
        await poll.refresh()
        self.assertIn("alice", ve.get_votes_for_element(element_key))

        await self.cog.reset_votes(self.cog, self.ctx)

        await poll.refresh()
        with self.assertRaises(ElementNotInVotesDict):
            ve.get_votes_for_element(element_key)

    async def test_reset_votes_non_admin(self):
        """Test the reset_votes command with a non admin."""
        self.assertFalse(await is_admin(self.db, self.ctx, self.ctx.author.id))
        # Reset the context to remove super admin messages
        self.__set_context()

        # Find the poll and reset votes
        poll = await Poll.find(self.db, self.ctx.channel, create_if_not_exist=True)

        button_id = poll.get_games_button_ids_list()[0]
        element_key = poll.button_id_to_element_key(button_id)

        ve = VotersEngine(poll)
        await ve.toggle_vote(self.user, button_id)
        await poll.refresh()
        self.assertIn("alice", ve.get_votes_for_element(element_key))

        await self.cog.reset_votes(self.cog, self.ctx)

        await poll.refresh()
        self.assertIn("alice", ve.get_votes_for_element(element_key))

        self.send.assert_called_once_with(content="You do not have the privilege to do that", ephemeral=True,
                                          delete_after=15)

    async def test_schedule_polls_admin(self):
        """Test the schedule_polls command with an admin."""
        # Ensure the user has admin rights
        await self.set_admin(self.ctx.author.id)
        self.assertTrue(await is_admin(self.db, self.ctx, self.ctx.author.id))

        poll = await Poll.find(self.db, self.ctx.channel, create_if_not_exist=True)

        # Schedule the poll
        day = 3
        await self.cog.schedule_polls(self.cog, self.ctx, day)

        poll_dict = await self.db.poll_instances.find_one({KEY: poll.key})
        self.assertEqual(3, poll_dict["misc"]["schedule"])


if __name__ == "__main__":
    unittest.main()
