import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import Mock

from libs.admin.admin import grant
from libs.admin.admin import super_admin
from libs.dat.guild import Guild
from libs.guilds.guilds_cog import GuildsCog
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

        self.user_id = 94030
        self.user = Mock(name="Test User", id=self.user_id)
        self.discord_guild = Mock(name="Test Guild", id=123456)
        self.discord_channel = AsyncMock(name="Test Channel", guild=self.discord_guild, me=self.user, author=self.user)
        self.context = AsyncMock(name="Test Context", channel=self.discord_channel, interaction=self.discord_channel,
                                 me=self.user, author=self.user)

        self.bot = Mock(name="Test Bot")
        self.gc = gc = GuildsCog(self.bot, self.db)

    async def test_guild_find_or_create(self):
        guild = await Guild.find_or_create(self.db, self.discord_channel)

        self.assertEqual("123456", guild.key)

        self.assertIn("adg", guild.games.keys())
        self.assertIn("adg", guild.poll_default)

    async def test_guild_vote_count(self):
        guild = await Guild.find_or_create(self.db, self.discord_channel)
        await guild.count_vote(self.discord_channel, "adg")

        existing_record = await self.db.guilds.find_one({"key": "123456"})
        self.assertEqual(1, existing_record["games"]["adg"]["votes"])

    async def test_guild_reset_command_not_available_for_common_users(self):
        await self.gc.reset_guild.callback(self.gc, self.context)

        self.context.send.assert_awaited()
        self.context.send.assert_awaited_with(
            content='You do not have the privilege to do that', ephemeral=True, delete_after=15)

    async def test_guild_reset_command_not_available_for_admin(self):
        await grant(self.db, self.discord_channel, self.user_id)

        await self.gc.reset_guild.callback(self.gc, self.context)

        self.context.send.assert_awaited()
        self.context.send.assert_awaited_with(
            content='You do not have the privilege to do that', ephemeral=True, delete_after=15)

    async def test_guild_reset_command_available_for_super_admin_and_do_actually_reset_guild(self):
        await Guild.find_or_create(self.db, self.discord_channel)

        filter_condition = {'key': '123456'}
        update_operation = {'$set': {'games.dune.long': 'foo'}}
        result = await self.db.guilds.update_many(filter_condition, update_operation)
        self.assertTrue(result)

        await super_admin(self.db, self.context)

        gc = GuildsCog(Mock(), self.db)
        await gc.reset_guild.callback(gc, self.context)

        filter_condition = {'key': '123456', 'games.dune.long': 'foo'}
        result = await self.db.guilds.find_one(filter_condition)
        self.assertFalse(result)
