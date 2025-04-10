import unittest
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock

from discord import Message

from poll.orm.helpers.polls.rebuild_buttons import rebuild_buttons
from poll.orm.helpers.polls.votes import add_vote, remove_vote, reset_votes, toggle_vote
from tests.base import BotTest


class TestPolls(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_votes(self):
        poll = await rebuild_buttons(self.poll)

        button_key = list(poll.buttons.keys())[0]
        # Add vote
        poll = await add_vote(poll, button_key, 123)
        self.assertIn(123, poll.buttons[button_key].votes.votes)

        # Vote is added only once
        poll = await add_vote(poll, button_key, 123)
        self.assertEqual(1, len(poll.buttons[button_key].votes.votes))

        # Second add
        poll = await add_vote(poll, button_key, 456)
        self.assertIn(456, poll.buttons[button_key].votes.votes)

        # Remove first
        poll = await remove_vote(poll, button_key, 123)
        self.assertNotIn(123, poll.buttons[button_key].votes.votes)
        self.assertIn(456, poll.buttons[button_key].votes.votes)

        # Test reset votes
        poll, self.guild = await reset_votes(poll, self.guild)
        self.assertEqual([], poll.buttons[button_key].votes.votes)

        # Toggle vote
        poll = await toggle_vote(poll, button_key, 123)
        self.assertIn(123, poll.buttons[button_key].votes.votes)

        poll = await toggle_vote(poll, button_key, 456)
        self.assertIn(456, poll.buttons[button_key].votes.votes)

        poll = await toggle_vote(poll, button_key, 123)
        self.assertNotIn(123, poll.buttons[button_key].votes.votes)

    async def test_get_poll_lines(self):
        poll = await rebuild_buttons(self.poll)

        button_key_1 = list(poll.buttons.keys())[0]
        button_key_2 = list(poll.buttons.keys())[1]
        button_key_3 = list(poll.buttons.keys())[2]
        button_key_last = list(poll.buttons.keys())[-1]

        # Add vote
        poll = await add_vote(poll, button_key_1, 123)
        poll = await add_vote(poll, button_key_1, 456)

        poll = await add_vote(poll, button_key_2, 123)
        poll = await add_vote(poll, button_key_3, 456)

        poll = await add_vote(poll, button_key_last, 123)
        poll = await add_vote(poll, button_key_last, 456)

        message = AsyncMock(spec=Message, guild=Mock(get_member=lambda user_id: Mock(display_name=user_id)))
        # result = await get_poll_lines(message, poll)

        # print()
        # for e in result:
        #     print(e)
