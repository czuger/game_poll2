import unittest

from poll.commands_response.add_game_to_guild import add_game_to_guild
from poll.orm.game_orm_object import get_game_short
from tests.base import BotTest


class TestAddGameToGuild(unittest.IsolatedAsyncioTestCase, unittest.TestCase, BotTest):
    async def asyncSetUp(self):
        await self.set_up()
        # # Mock the Guild object
        # self.guild = MagicMock()
        # self.guild.key = "test_guild"
        #
        # # Mock the DbConnector object
        # self.db = MagicMock()
        # self.db.guilds.find_one = AsyncMock()
        # self.db.guilds.update_one = AsyncMock()
        #
        # # Mock game name
        # self.game_name = "Test Game"

    async def test_add_game_success(self):
        (self.params_b, added) = await add_game_to_guild(self.params_b, "foo bar")

        self.assertTrue(added)
        self.assertEqual("foo bar", await get_game_short("foo_bar"))

    async def test_add_temporary_game_already_exists(self):
        (self.params_b, added) = await add_game_to_guild(self.params_b, "foo bar")
        (self.params_b, added) = await add_game_to_guild(self.params_b, "foo bar")

        self.assertFalse(added)
        self.assertEqual("foo bar", await get_game_short("foo_bar"))
