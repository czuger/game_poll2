import unittest
from unittest.async_case import IsolatedAsyncioTestCase

from poll.orm import GuildOrmObject
from poll.orm.game_orm_object import check_games_at_startup
from tests.base import BotTest


class TestGamesAndGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

        await check_games_at_startup()

    async def test_add_guild(self):
        guild = GuildOrmObject(key="123456")
        await guild.insert()

        self.assertIn("adg", guild.games)
        self.assertIn("saga", guild.games)
