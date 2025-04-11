import unittest
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from poll.cogs import AdminManagementCog
from poll.commands_response.admin import super_admin
from poll.misc import ADMINS_LOG_NAME
from tests.base import BotTest


class TestAdminManagementCog(unittest.IsolatedAsyncioTestCase, unittest.TestCase, BotTest):
    def setUp(self):
        # Mock bot instance
        self.set_up()

        self.bot = MagicMock()
        self.cog = AdminManagementCog(self.bot, self.db)

        self.author = MagicMock(id="my_user_id")
        self.ctx = AsyncMock(author=self.author)  # Mock the command context

    # TODO : when user do not exist, grant, upgrade or downgrade should fail.
    # Not create the user.
    async def test_grant(self):
        await super_admin(self.db, self.ctx)
        with self.assertLogs(ADMINS_LOG_NAME, level="DEBUG") as log:
            await self.cog.grant(self.cog, self.ctx, "some_user")

            self.assertIn('INFO:admins:Granted admin rights to user some_user.', log[1])

    async def test_upgrade(self):
        await super_admin(self.db, self.ctx)
        with self.assertLogs(ADMINS_LOG_NAME, level="DEBUG") as log:
            await self.cog.upgrade(self.cog, self.ctx, "some_user")

        self.assertIn('INFO:admins:Upgraded user some_user to super admin.', log[1])

    async def test_downgrade(self):
        await super_admin(self.db, self.ctx)
        with self.assertLogs(ADMINS_LOG_NAME, level="DEBUG") as log:
            await self.cog.downgrade(self.cog, self.ctx, "some_user")

        self.assertIn('INFO:admins:Downgraded user some_user from super admin to regular admin.', log[1])

    async def test_revoke(self):
        await super_admin(self.db, self.ctx)
        with self.assertLogs(ADMINS_LOG_NAME, level="DEBUG") as log:
            await self.cog.revoke(self.cog, self.ctx, "some_user")

        self.assertIn('INFO:admins:Revoked admin rights from user some_user.', log[1])

    async def test_super_admin(self):
        await super_admin(self.db, self.ctx)
        with self.assertLogs(ADMINS_LOG_NAME, level="DEBUG") as log:
            await self.cog.super_admin(self.cog, self.ctx)

        self.assertIn('INFO:admins:Super admin already defined. Command invoked by my_user_id.', log[1])


if __name__ == "__main__":
    unittest.main()
