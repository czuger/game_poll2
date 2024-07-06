import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from libs.dat.guild import Guild
from libs.gamebot_commands import reset_guild_cmd
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_guild_find_or_create(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild)

        guild = await Guild.find_or_create(self.db, discord_channel)

        self.assertEqual("123456", guild.key)

        self.assertIn("adg", guild.games.keys())
        self.assertIn("adg", guild.poll_default)

    async def test_guild_reset(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild)

        guild = await Guild.find_or_create(self.db, discord_channel)
        # await self.db.guilds.update_one(filter={"key": 123456}, update={"$set": {}})

        guild.games = None
        guild.miniatures = None
        guild.poll_default = None
        guild.boards = None

        query = {"key": 123456}
        existing_record = await self.db.guilds.find_one(query)
        self.assertFalse(existing_record)

        await guild.reset()

        self.assertEqual("123456", guild.key)

        self.assertIn("adg", guild.games.keys())
        self.assertIn("adg", guild.poll_default)

    async def test_guild_reset_command(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild)

        await reset_guild_cmd(discord_channel, self.db)
