import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, Mock

import discord
from discord import Guild

from poll.interfaces.poll.poll_embedding import get_players_embed
from poll.orm.helpers.polls.votes import toggle_vote
from tests.base import BotTest


class TestPollEmbedding(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_embedding(self):
        user = MagicMock(id=654321, display_name="foo")
        discord_guild = MagicMock(spec=Guild, id=123456, get_member=Mock())
        discord_guild.get_member.return_value = user

        element_key_1 = list(self.poll.poll_elements.keys())[0]
        await toggle_vote(self.poll, element_key_1, user.id)

        self.params_b.discord_guild_object = discord_guild
        embed = await get_players_embed(self.params_b)
        self.assertIsInstance(embed, discord.Embed)
