import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from poll.cogs.guilds_cog import GuildsCog
from poll.commands_response.admin import grant
from poll.commands_response.admin import super_admin
from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.helpers.guilds.getters import find_or_create_guild
from poll.orm.helpers.polls.votes import toggle_vote
from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

        # self.user_id = 94030
        # self.user = Mock(name="Test User", id=self.user_id)
        # self.discord_guild = Mock(name="Test Guild", id=123456)
        # self.discord_channel = AsyncMock(name="Test Channel", guild=self.discord_guild, me=self.user, author=self.user)
        # self.context = AsyncMock(name="Test Context", channel=self.discord_channel, interaction=self.discord_channel,
        #                          me=self.user, author=self.user)
        #
        # self.bot = Mock(name="Test Bot")
        # self.gc = gc = GuildsCog(self.bot, self.db)

    async def test_guild_find_or_create(self):
        guild = await find_or_create_guild(456789)

        self.assertEqual(456789, guild.key)

        self.assertIn("adg", guild.games)
        self.assertIn("adg", guild.poll_default_games)

        newly_created_guild = GuildOrmObject.find_one(GuildOrmObject.key == 456789)
        self.assertTrue(newly_created_guild)

    async def test_guild_vote_count(self):
        await toggle_vote(self.params_b, "adg", 123)
        await toggle_vote(self.params_b, "adg", 456)

        self.assertEqual(2, self.params_b.guild.total_votes_data["adg"].total_votes_count)

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
        await Guild.find_or_create_by_channel(self.db, self.discord_channel)

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
