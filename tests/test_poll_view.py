import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from unittest.mock import Mock

import discord

from libs.poll.poll import Poll
from libs.poll.poll_view import PollView
from tests.base import BotTest


class TestPollView(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_poll_view(self):
        user = MagicMock(display_name="foo")
        discord_guild = MagicMock(id=123456, get_member=Mock())
        discord_guild.get_member.return_value = user
        discord_channel = MagicMock(id=123456, guild=discord_guild)

        poll = await Poll.find_or_create(self.db, discord_channel)

        pv = PollView()
        poll_view = await pv.initialize_view(self.db, poll)
        self.assertIsInstance(poll_view, discord.ui.view.View)
