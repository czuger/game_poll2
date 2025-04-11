import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock

import discord
from discord import User, Guild, Interaction

from poll.interfaces.poll.helpers.build_buttons_list import PollButtonElement
from poll.interfaces.poll.poll_button import PollButton
from poll.orm.poll_orm_object import PollOrmObject
from tests.base import BotTest


class TestPollButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_poll_button(self):
        user = MagicMock(spec=User, id=252627, display_name="foo")

        discord_guild = MagicMock(spec=Guild, id=123456)
        discord_guild.get_member = MagicMock(return_value=user)

        message = AsyncMock(edit=AsyncMock())
        message.edit.return_value = 0

        response = AsyncMock(defer=AsyncMock())
        response.defer.return_value = 0

        interaction = MagicMock(spec=Interaction, user=user, message=message, response=response, guild=discord_guild)

        self.poll: PollOrmObject

        # Toggle first button (should be game)
        button_id = list(self.poll.buttons)[0]
        button = PollButtonElement(key=button_id, short_str="foo", row=0)
        pb = PollButton(self.poll, button)
        await pb.callback(interaction)
        self.assertIsInstance(pb, discord.ui.Button)

        # Toggle last button (should be other)
        button_id = list(self.poll.buttons)[-1]
        button = PollButtonElement(key=button_id, short_str="foo", row=0)

        pb = PollButton(self.poll, button)
        await pb.callback(interaction)
        self.assertIsInstance(pb, discord.ui.Button)
