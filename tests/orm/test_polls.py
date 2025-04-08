import unittest
from unittest.async_case import IsolatedAsyncioTestCase

from poll.orm.poll_orm_object import PollOrmObject
from tests.base import BotTest


class TestPolls(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_votes(self):
        poll = PollOrmObject(key="123456")

        await poll.insert()

        # Add game
        button_key = await poll.add_game("adg")

        # Add vote
        await poll.add_vote(button_key, "123")
        self.assertIn("123", poll.buttons[button_key].votes)

        # Vote is added only once
        await poll.add_vote(button_key, "123")
        self.assertEqual(1, len(poll.buttons[button_key].votes))

        # Second add
        await poll.add_vote(button_key, "456")
        self.assertIn("456", poll.buttons[button_key].votes)

        # Remove first
        await poll.remove_vote(button_key, "123")
        self.assertNotIn("123", poll.buttons[button_key].votes)
        self.assertIn("456", poll.buttons[button_key].votes)
