import unittest
from unittest import IsolatedAsyncioTestCase

import discord

from poll.interfaces.add_game.respond_to_add_game_button import RespondToAddGameButton
from poll.interfaces.poll.helpers.build_poll_button_element import build_poll_button_element
from poll.misc.objects import ButtonType
from poll.orm.game_orm_object import GameOrmObject
from tests.base import BotTest


class TestRespondToAddGameButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_add_game_button(self):
        cursor = GameOrmObject.find_all()
        games = await cursor.to_list(length=None)
        games_keys = [e.key for e in games]

        self.params_b.guild.games = games_keys
        self.params_b.guild.save()

        button_element = await build_poll_button_element(self.params_b, ButtonType.OTHER, "add", 4)

        pb = RespondToAddGameButton(self.params_b, button_element)
        await pb.callback(self.interaction)
        self.assertIsInstance(pb, discord.ui.Button)

        self.assertEqual(2, len(self.interaction.user.method_calls))
        self.assertEqual(25, len(self.interaction.user.method_calls[0][2]["view"].children))
