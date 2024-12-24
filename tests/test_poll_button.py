import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import discord

from poll.libs.objects.poll import Poll
from poll.libs.poll.poll_buttons import PollButton
from tests.base import BotTest


class TestPollButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_poll_button(self):
        user = MagicMock(id=252627, display_name="foo")

        discord_guild = MagicMock(id=123456, get_member=Mock())
        discord_guild.get_member.return_value = user

        discord_channel = MagicMock(id=123456, guild=discord_guild)

        message = AsyncMock(edit=AsyncMock())
        message.edit.return_value = 0

        response = AsyncMock(defer=AsyncMock())
        response.defer.return_value = 0

        interaction = MagicMock(channel=discord_channel, user=user, message=message, response=response)

        # Toggle first button (should be game)
        poll = await Poll.find(self.db, discord_channel, create_if_not_exist=True)
        button_id = list(poll.games.keys())[0]

        pb = PollButton(self.db, poll, "foo", button_id, 0)
        await pb.callback(interaction)
        self.assertIsInstance(pb, discord.ui.Button)

        # Toggle last button (should be other)
        poll = await Poll.find(self.db, discord_channel)
        button_id = list(poll.games.keys())[-1]

        pb = PollButton(self.db, poll, "foo", button_id, 0)
        await pb.callback(interaction)
        self.assertIsInstance(pb, discord.ui.Button)
