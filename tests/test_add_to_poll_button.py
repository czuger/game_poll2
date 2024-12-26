import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import discord
from discord import Interaction, Message, TextChannel, InteractionResponse

from poll.libs.interfaces.add_game.add_to_poll_button import AddToPollButton
from poll.libs.interfaces.helpers.buttons import make_btn_key
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll
from tests.base import BotTest


class TestAddToPollButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_add_to_poll_button(self):
        user = AsyncMock(id=252627, display_name="foo")

        discord_guild = AsyncMock(spec=Guild, id="my_guild", get_member=Mock())
        discord_guild.get_member.return_value = user

        chat_discord_channel = MagicMock(spec=TextChannel, id="chat_channel", guild=discord_guild)
        poll_discord_channel = MagicMock(spec=TextChannel, id="poll_channel", guild=discord_guild)

        message = AsyncMock(spec=Message, edit=AsyncMock())
        message.edit.return_value = 0

        response = AsyncMock(spec=InteractionResponse, defer=AsyncMock())
        response.defer.return_value = 0

        interaction = AsyncMock(spec=Interaction, channel=chat_discord_channel, user=user, message=message,
                                response=response)

        poll = await Poll.find(self.db, poll_discord_channel, create_if_not_exist=True)

        guild = await Guild.find_or_create_by_channel(self.db, poll_discord_channel)
        game_key = list(guild.poll_default)[0]
        button_id = make_btn_key(game_key, "g")

        pb = AddToPollButton(self.db, guild, poll, message, "foo", button_id, 0)
        await pb.callback(interaction)
        self.assertIsInstance(pb, discord.ui.Button)

        buttons_keys = [e["key"] for e in poll.games.values()]
        self.assertIn(game_key, buttons_keys)
