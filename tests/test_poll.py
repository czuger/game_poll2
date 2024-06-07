import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from unittest.mock import Mock

from libs.poll.poll import Poll
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_buttons_keys_format(self):
        # First testing creation
        discord_channel = Mock(id=123456, guild=Mock(id=123456))
        poll = await Poll.find_or_create(self.db, discord_channel)

        self.assertIn("o_other", [e[0:len("o_other")] for e in poll.buttons["others"].keys()])
        self.assertIn("g_adg", [e[0:len("g_adg")] for e in poll.games.keys()])

    async def test_poll(self):
        # First testing creation
        discord_channel = MagicMock(id=123456)
        poll = await Poll.find_or_create(self.db, discord_channel)

        self.assertEqual("123456", poll.key)
        self.assertIn("g_frostgrave", [e[0:len("g_frostgrave")] for e in poll.games.keys()])

        # Entry exist, testing find
        poll = await Poll.find_or_create(self.db, discord_channel)
        self.assertEqual("123456", poll.key)

        # No testing button toggle
        button_id = list(poll.games.keys())[0]
        game_key = poll.games[button_id]
        user = Mock(id=654321)

        poll.toggle_button_id(user, button_id)
        poll_db_object = poll.get_poll_db_object()

        self.assertIn("654321", poll_db_object["buttons"]["games"][button_id]["players"])

        poll.toggle_button_id(user, button_id)
        poll_db_object = poll.get_poll_db_object()

        self.assertNotIn("654321", poll_db_object["buttons"]["games"][button_id]["players"])

        poll.toggle_button_id(user, button_id)
        poll_db_object = poll.get_poll_db_object()

        self.assertIn("654321", poll_db_object["buttons"]["games"][button_id]["players"])
        