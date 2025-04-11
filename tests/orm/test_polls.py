import unittest
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock

from discord import Message

from poll.orm.helpers.polls.votes import add_vote, remove_vote, reset_votes, toggle_vote
from tests.base import BotTest


class TestPolls(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_votes(self):
        element_key = list(self.poll.poll_elements.keys())[0]
        # Add vote
        self.poll = await add_vote(self.poll, element_key, 123)
        self.assertIn(123, self.poll.poll_elements[element_key].votes.votes)

        # Vote is added only once
        self.poll = await add_vote(self.poll, element_key, 123)
        self.assertEqual(1, len(self.poll.poll_elements[element_key].votes.votes))

        # Second add
        self.poll = await add_vote(self.poll, element_key, 456)
        self.assertIn(456, self.poll.poll_elements[element_key].votes.votes)

        # Remove first
        self.poll = await remove_vote(self.poll, element_key, 123)
        self.assertNotIn(123, self.poll.poll_elements[element_key].votes.votes)
        self.assertIn(456, self.poll.poll_elements[element_key].votes.votes)

        # Test reset votes
        self.params_b = await reset_votes(self.params_b)
        self.assertEqual([], self.poll.poll_elements[element_key].votes.votes)

        # Toggle vote
        self.poll = await toggle_vote(self.poll, element_key, 123)
        self.assertIn(123, self.poll.poll_elements[element_key].votes.votes)

        self.poll = await toggle_vote(self.poll, element_key, 456)
        self.assertIn(456, self.poll.poll_elements[element_key].votes.votes)

        self.poll = await toggle_vote(self.poll, element_key, 123)
        self.assertNotIn(123, self.poll.poll_elements[element_key].votes.votes)

    async def test_get_poll_lines(self):
        element_key_1 = list(self.poll.poll_elements.keys())[0]
        element_key_2 = list(self.poll.poll_elements.keys())[1]
        element_key_3 = list(self.poll.poll_elements.keys())[2]
        element_key_last = list(self.poll.poll_elements.keys())[-1]

        # Add vote
        self.poll = await add_vote(self.poll, element_key_1, 123)
        self.poll = await add_vote(self.poll, element_key_1, 456)

        self.poll = await add_vote(self.poll, element_key_2, 123)
        self.poll = await add_vote(self.poll, element_key_3, 456)

        self.poll = await add_vote(self.poll, element_key_last, 123)
        self.poll = await add_vote(self.poll, element_key_last, 456)

        message = AsyncMock(spec=Message, guild=Mock(get_member=lambda user_id: Mock(display_name=user_id)))
        # result = await get_poll_lines(message, poll)

        # print()
        # for e in result:
        #     print(e)
