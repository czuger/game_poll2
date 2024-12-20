import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from discord.ext.commands import Context

from poll.libs.games.games_cog import GamesCog
from tests.base import BotTest


class TestGamesCog(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):
    def setUp(self):
        # Mock bot instance
        self.set_up()

        self.bot = MagicMock()
        self.cog = GamesCog(self.bot, self.db)

    async def test_add_game_success(self):
        # Setup mocks
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.channel = MagicMock()
        mock_ctx.send = AsyncMock()

        # Run the coroutine
        game_name = "example_game"

        await self.cog.add_game(self.cog, mock_ctx, game_name=game_name)

        # Verify calls
        mock_ctx.send.assert_any_await("Le jeu a bien été ajouté.", delete_after=120)
        mock_ctx.send.assert_any_await("Vous devez encore l'ajouter aux sondages avec le bouton 🧩 Ajouter",
                                       delete_after=120)

    async def test_add_game_already_exists(self):
        # Setup mocks
        mock_ctx = MagicMock(spec=Context)
        mock_ctx.channel = MagicMock()
        mock_ctx.send = AsyncMock()

        # Run the coroutine
        game_name = "adg"

        await self.cog.add_game(self.cog, mock_ctx, game_name=game_name)

        # Verify calls
        mock_ctx.send.assert_awaited_once_with("Ce jeu existe déjà.", delete_after=120)


if __name__ == "__main__":
    unittest.main()
