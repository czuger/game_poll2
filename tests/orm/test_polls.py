import unittest
from unittest.async_case import IsolatedAsyncioTestCase

from poll.libs.orm.poll_orm_object import PollOrmObject
from tests.base import BotTest


class TestPolls(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_votes(self):
        poll = PollOrmObject(key="123456")

        await poll.insert()

        # Add vote
        await poll.add_vote("adg", "123")
        self.assertIn("123", poll.votes["adg"])

        # Vote is added only once
        await poll.add_vote("adg", "123")
        self.assertEqual(1, len(poll.votes["adg"]))

        # Second add
        await poll.add_vote("adg", "456")
        self.assertIn("456", poll.votes["adg"])

        # Remove first
        await poll.remove_vote("adg", "123")
        self.assertNotIn("123", poll.votes["adg"])
        self.assertIn("456", poll.votes["adg"])

    async def test_remove_vote_from_non_existing_dont_blow(self):
        poll = PollOrmObject(key="123456")

        await poll.insert()
        await poll.remove_vote("adg", "123")

        self.assertNotIn("adg", poll.votes)
