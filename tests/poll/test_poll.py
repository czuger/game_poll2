import unittest
from unittest import IsolatedAsyncioTestCase

from poll.orm.helpers.polls.votes import toggle_vote
from tests.base import BotTest


class TestPoll(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll(self):
        self.params_b = await toggle_vote(self.params_b, "adg", 123)
        self.assertIn(123, self.params_b.poll.poll_elements["adg"].votes.votes)

        self.params_b = await toggle_vote(self.params_b, "adg", 123)
        self.assertNotIn(123, self.params_b.poll.poll_elements["adg"].votes.votes)

        self.params_b = await toggle_vote(self.params_b, "adg", 123)
        self.assertIn(123, self.params_b.poll.poll_elements["adg"].votes.votes)
