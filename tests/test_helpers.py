import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from libs.dat.guild import Guild
from libs.helpers.buttons import get_key_from_btn
from libs.helpers.buttons import make_btn_key
from tests.base import BotTest


class TestHelpers(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_get_key_from_btn(self):
        discord_guild = MagicMock(id=123456)
        discord_channel = MagicMock(guild=discord_guild)

        guild = await Guild.find_or_create(self.db, discord_channel)

        for k in guild.poll_default:
            self.assertEqual(k, get_key_from_btn(make_btn_key(k, "g")))
