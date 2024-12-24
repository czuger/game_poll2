import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import Mock

from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_buttons_keys_format(self):
        # First testing creation
        discord_channel = Mock(id=123456, guild=Mock(id=123456))
        poll = await Poll.find(self.db, discord_channel, create_if_not_exist=True)

        self.assertIn("o_other", [e[0:len("o_other")] for e in poll.others.keys()])
        self.assertIn("g_adg", [e[0:len("g_adg")] for e in poll.games.keys()])

    async def test_poll(self):
        # First testing creation
        discord_guild = AsyncMock(id=123456)
        discord_channel = Mock(id=123456, guild=discord_guild)

        guild = await Guild.find_or_create(self.db, discord_channel)
        poll = await Poll.find(self.db, discord_channel, create_if_not_exist=True)

        self.assertEqual("123456", poll.key)
        self.assertIn("g_frostgrave", [e[0:len("g_frostgrave")] for e in poll.games.keys()])

        # Entry exist, testing find
        poll = await Poll.find(self.db, discord_channel)
        self.assertEqual("123456", poll.key)

        # No testing button toggle
        button_id = list(poll.games)[0]
        user = Mock(id=654321)
        mock_interaction = Mock(user=user)

        await poll.toggle_button_id(mock_interaction, button_id)
        await poll.refresh()
        game_key = poll.games[button_id]["key"]
        self.assertIn("654321", poll.votes[game_key])

        query = {"guild_id": "123456", "votes": {"$elemMatch": {"gk": game_key}}}
        result = await self.db.db.votes.find_one(query)
        self.assertTrue(result)

        await poll.toggle_button_id(mock_interaction, button_id)
        await poll.refresh()
        self.assertNotIn("654321", poll.votes[game_key])

        await poll.toggle_button_id(mock_interaction, button_id)
        await poll.refresh()
        self.assertIn("654321", poll.votes[game_key])
