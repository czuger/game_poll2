import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

from libs.admin.admin import grant, upgrade, is_admin, is_super_admin, downgrade, revoke, super_admin
from tests.base import BotTest


class TestAdmin(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    def setUp(self):
        self.set_up()

    async def test_admin(self):
        admin_user = MagicMock(id=252627, display_name="AdminUserMock")

        discord_guild = MagicMock(id=123456, get_member=Mock())
        discord_guild.get_member.return_value = admin_user

        discord_channel = MagicMock(id=123456, guild=discord_guild)

        message = AsyncMock(edit=AsyncMock())
        # message.edit.return_value(0)

        response = AsyncMock(defer=AsyncMock())
        # response.defer.return_value(0)

        ctx = AsyncMock(channel=discord_channel, author=admin_user, user=admin_user, message=message,
                        response=response)

        await super_admin(self.db, ctx)

        await grant(self.db, ctx, 123456)
        status = await is_admin(self.db, ctx, 123456)
        self.assertTrue(status)
        status = await is_super_admin(self.db, ctx, 123456)
        self.assertFalse(status)

        await upgrade(self.db, ctx, 123456)
        status = await is_super_admin(self.db, ctx, 123456)
        self.assertTrue(status)

        await downgrade(self.db, ctx, 123456)
        status = await is_super_admin(self.db, ctx, 123456)
        self.assertFalse(status)
        status = await is_admin(self.db, ctx, 123456)
        self.assertTrue(status)

        await revoke(self.db, ctx, 123456)
        status = await is_super_admin(self.db, ctx, 123456)
        self.assertFalse(status)
        status = await is_admin(self.db, ctx, 123456)
        self.assertFalse(status)
