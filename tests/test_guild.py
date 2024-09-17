import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from unittest.mock import Mock

from libs.dat.guild import Guild
from libs.guilds.guilds_cog import GuildsCog
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

    async def test_guild_reset_command(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild, me=Mock(id=1))

        await GuildsCog.reset_guild(discord_channel, self.db)

    async def test_guild_vote_count(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild)

        guild = await Guild.find_or_create(self.db, discord_channel)
        await guild.count_vote(discord_channel, "adg")

        existing_record = await self.db.guilds.find_one({"key": "123456"})
        self.assertEqual(1, existing_record["games"]["adg"]["votes"])
