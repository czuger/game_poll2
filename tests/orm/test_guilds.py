import unittest
from unittest.async_case import IsolatedAsyncioTestCase

from tests.base import BotTest


class TestGuild(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_add_guild(self):
        self.assertIn("adg", self.guild.games)
        self.assertIn("saga", self.guild.games)
