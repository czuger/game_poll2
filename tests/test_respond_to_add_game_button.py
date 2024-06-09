import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import discord

from libs.add_game.respond_to_add_game_button import RespondToAddGameButton
from libs.dat.guild import Guild
from libs.helpers.buttons import make_btn_key
from libs.poll.poll import Poll
from tests.base import BotTest


class TestRespondToAddGameButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_add_game_button(self):
        user = AsyncMock(id=252627, display_name="foo")

        discord_guild = AsyncMock(id=123456, get_member=Mock())
        discord_guild.get_member.return_value = user

        discord_channel = MagicMock(id=123456, guild=discord_guild)

        message = AsyncMock(edit=AsyncMock())
        message.edit.return_value(0)

        response = AsyncMock(defer=AsyncMock())
        response.defer.return_value(0)

        interaction = AsyncMock(channel=discord_channel, user=user, message=message, response=response)

        # Toggle first button (should be game)
        poll = await Poll.find(self.db, discord_channel, create_if_not_exist=True)
        guild = await Guild.find_or_create(self.db, discord_channel)
        game_key = list(guild.games["boards"].keys())[0]
        button_id = make_btn_key(game_key, "g")

        pb = RespondToAddGameButton(self.db, poll, "foo", button_id, 0)
        await pb.callback(interaction)
        self.assertIsInstance(pb, discord.ui.Button)
