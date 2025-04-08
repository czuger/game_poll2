import unittest
from unittest.async_case import IsolatedAsyncioTestCase

from poll.orm.game_orm_object import GameOrmObject, check_games_at_startup, get_game
from tests.base import BotTest


class TestGamesAndGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

        await check_games_at_startup()

    async def test_find_game(self):
        game1 = await get_game("saga")
        game2 = await get_game("saga")
        game3 = await get_game("adg")

        self.assertEqual("Saga", game1.long)
        self.assertEqual("Saga", game2.long)
        self.assertEqual("Art de la guerre", game3.long)

    async def test_add_games(self):
        game1 = GameOrmObject(key="foo", long="Foo bar", short="foobar", game_type="Miniatures")

        await game1.insert()
        game2 = await get_game("foo")
        self.assertEqual("Foo bar", game2.long)
