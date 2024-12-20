import unittest
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from poll.libs.add_game.add_temporary_game import GameAlreadyExist
from poll.libs.add_game.add_temporary_game import add_temporary_game
from poll.libs.misc.replace_spaces_and_non_ansi import replace_spaces_and_non_ansi


class TestAddTemporaryGame(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Mock the Guild object
        self.guild = MagicMock()
        self.guild.key = "test_guild"

        # Mock the DbConnector object
        self.db = MagicMock()
        self.db.guilds.find_one = AsyncMock()
        self.db.guilds.update_one = AsyncMock()

        # Mock game name
        self.game_name = "Test Game"

    async def test_add_temporary_game_success(self):
        # Configure mock for no existing game
        self.db.guilds.find_one.return_value = None

        # Run the function
        await add_temporary_game(self.guild, self.db, self.game_name)

        # Assertions
        new_game_key = replace_spaces_and_non_ansi(self.game_name)
        self.db.guilds.find_one.assert_awaited_once_with({"key": self.guild.key}, {f"games.{new_game_key}": 1})

        self.db.guilds.update_one.assert_awaited_once_with(
            {"key": self.guild.key},
            {"$set": {f"games.{new_game_key}": {
                "key": new_game_key,
                "long": self.game_name,
                "short": self.game_name,
                "temporary": True,
                "add_timestamp": unittest.mock.ANY
            }}}
        )

    async def test_add_temporary_game_already_exists(self):
        # Configure mock for existing game
        existing_game_key = replace_spaces_and_non_ansi(self.game_name)
        self.db.guilds.find_one.return_value = {"games": {existing_game_key: {}}}

        # Run the function and assert exception
        with self.assertRaises(GameAlreadyExist):
            await add_temporary_game(self.guild, self.db, self.game_name)

        # Assertions
        self.db.guilds.find_one.assert_awaited_once_with({"key": self.guild.key}, {f"games.{existing_game_key}": 1})
        self.db.guilds.update_one.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
