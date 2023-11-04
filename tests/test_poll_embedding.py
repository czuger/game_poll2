import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from unittest.mock import Mock

import discord

from libs.poll import Poll
from tests.base import BotTest
from libs.poll_embedding import get_players_embed


class TestPollEmbedding(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_poll_embedding(self):
        user = MagicMock(display_name="foo")
        discord_guild = MagicMock(id=123456, get_member=Mock())
        discord_guild.get_member.return_value = user
        discord_channel = MagicMock(id=123456, guild=discord_guild)

        poll = await Poll.find_or_create(self.db, discord_channel)

        # Embed with at least one user
        game_key = list(poll.games.keys())[0]
        user = MagicMock(id=654321)
        poll.toggle_button_id(user, game_key)

        embed = await get_players_embed(self.db, discord_channel)
        self.assertIsInstance(embed, discord.Embed)
