import unittest
from unittest.async_case import IsolatedAsyncioTestCase

from beanie import WriteRules

from poll.libs.orm.game_orm_object import GameOrmObject
from poll.libs.orm.guild_orm_object import GuildOrmObject
from tests.base import BotTest


class TestGamesAndGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_add_games(self):
        game1 = GameOrmObject(key="art_de_la_guerre", long="Art de la guerre", short="ADG", game_type="Miniatures")
        game2 = GameOrmObject(key="core_space", long="Core space", short="CSP", game_type="Miniatures")

        await game1.insert()
        await game2.create()

        result = await GameOrmObject.find_one(GameOrmObject.key == "art_de_la_guerre")
        self.assertEqual("Art de la guerre", result.long)

        result = await GameOrmObject.find_one(GameOrmObject.key == "core_space")
        self.assertEqual("Core space", result.long)

    async def test_add_games_and_guild(self):
        game1 = GameOrmObject(key="art_de_la_guerre", long="Art de la guerre", short="ADG", game_type="Miniatures")
        game2 = GameOrmObject(key="core_space", long="Core space", short="CSP", game_type="Miniatures")

        await game1.insert()
        await game2.insert()

        guild = GuildOrmObject(key="123456", games=[])

        await guild.insert()

        guild.games = [game1]
        await guild.save(link_rule=WriteRules.WRITE)

        guild.games = guild.games + [game2]
        await guild.save(link_rule=WriteRules.WRITE)

        self.assertIn("ADG", [e.short for e in guild.games])
        self.assertIn("CSP", [e.short for e in guild.games])
