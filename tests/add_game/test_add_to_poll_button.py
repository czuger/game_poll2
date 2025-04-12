import unittest
from unittest import IsolatedAsyncioTestCase

import discord

from poll.interfaces.add_game.add_to_poll_button import AddToPollButton
from poll.interfaces.poll.helpers.build_poll_button_element import build_poll_button_element
from poll.misc.objects import ButtonType
from poll.orm.game_orm_object import GameOrmObject
from tests.base import BotTest


class TestAddToPollButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_add_to_poll_button(self):
        cursor = GameOrmObject.find_all()
        games = await cursor.to_list(length=None)
        remaining_games_keys = [e.key for e in games]

        remaining_games_keys = list(set(remaining_games_keys) - set(self.params_b.poll.poll_elements.keys()))

        for i in range(20):
            key = str(remaining_games_keys.pop())
            button_element = await build_poll_button_element(self.params_b, ButtonType.GAME, key, 0)
            pb = AddToPollButton(self.params_b, button_element)
            await pb.callback(self.interaction)
            self.assertIsInstance(pb, discord.ui.Button)

            print(len(self.params_b.poll.poll_elements.keys()))
