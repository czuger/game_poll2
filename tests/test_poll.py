import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from libs.poll.poll import Poll
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_buttons_keys_format(self):
        # First testing creation
        discord_channel = MagicMock(id=123456)
        poll = await Poll.find_or_create(self.db, discord_channel)

        self.assertIn("BTNO_other", [e[0:10] for e in poll.buttons.keys()])
        self.assertIn("BTNG_lion_rampant", [e[0:17] for e in poll.buttons.keys()])

    async def test_poll(self):
        # First testing creation
        discord_channel = MagicMock(id=123456)
        poll = await Poll.find_or_create(self.db, discord_channel)

        self.assertEqual("123456", poll.key)
        self.assertIn("lion_rampant", [e[5:17] for e in poll.buttons.values()])

        # Entry exist, testing find
        poll = await Poll.find_or_create(self.db, discord_channel)
        self.assertEqual("123456", poll.key)

        # No testing button toggle
        button_id = list(poll.buttons.keys())[0]
        game_key = poll.buttons[button_id]
        user = MagicMock(id=654321)

        poll.toggle_button_id(user, button_id)
        poll_db_object = poll.get_poll_db_object()

        self.assertIn(game_key, poll_db_object[Poll.SELECTIONS_KEY])
        self.assertIn("654321", list(poll_db_object[Poll.SELECTIONS_KEY].values())[0])

        poll.toggle_button_id(user, button_id)
        poll_db_object = poll.get_poll_db_object()

        self.assertIn(game_key, poll_db_object[Poll.SELECTIONS_KEY])
        self.assertEqual([], list(poll_db_object[Poll.SELECTIONS_KEY].values())[0])

        poll.toggle_button_id(user, button_id)
        poll_db_object = poll.get_poll_db_object()

        self.assertIn(game_key, poll_db_object[Poll.SELECTIONS_KEY])
        self.assertIn("654321", list(poll_db_object[Poll.SELECTIONS_KEY].values())[0])
        