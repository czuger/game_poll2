import unittest
from unittest import IsolatedAsyncioTestCase

import discord

from poll.libs.interfaces.poll.poll_view import PollView
from tests.base import BotTest


class TestPollView(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_view(self):
        pv = PollView()
        poll_view = await pv.initialize_view(self.poll)
        self.assertIsInstance(poll_view, discord.ui.view.View)
