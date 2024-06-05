import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from unittest.mock import Mock

import discord

from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed
from tests.base import BotTest


class TestPollEmbedding(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_poll_embedding(self):
        user = MagicMock(display_name="foo")
        discord_guild = MagicMock(id=123456, get_member=Mock())
        discord_guild.get_member.return_value = user
        discord_channel = MagicMock(id=123456, guild=discord_guild)

        poll = await Poll.find(self.db, discord_channel, create_if_not_exist=True)

        # Embed with at least one user
        button_id = list(poll.games.keys())[0]
        user = MagicMock(id=654321)
        await poll.toggle_button_id(user, button_id)

        embed = await get_players_embed(self.db, discord_channel)
        self.assertIsInstance(embed, discord.Embed)
