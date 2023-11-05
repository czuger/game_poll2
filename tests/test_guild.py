import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from libs.guild import Guild
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_guild_find(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild)

        guild = await Guild.find_or_create(self.db, discord_channel)

        self.assertEqual("123456", guild.key)
        self.assertIn("lion_rampant", [e[5:17] for e in guild.games])
