import logging

from discord import Interaction
from discord import app_commands
from discord.ext import commands

from libs.dat.database import DbConnector

DELETE_TIME = 15
logger = logging.getLogger(__name__)


class AdminManagementCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db: DbConnector):
        self.bot = bot
        self.db = db

    async def send_message(self, interaction: Interaction, content: str):
        await interaction.response.send_message(content=content, ephemeral=True, delete_after=DELETE_TIME)

    async def ack_msg(self, interaction: Interaction):
        await self.send_message(interaction, "Done")

    async def error_msg(self, interaction: Interaction, exception: Exception):
        logger.error(f"Error during operation: {exception}")
        await self.send_message(interaction, "Error happened during operation")

    async def duplicate(self, interaction: Interaction):
        await self.send_message(interaction, "User already listed")

    async def not_found(self, interaction: Interaction, message="User is not admin"):
        await self.send_message(interaction, message)

    async def access_denied(self, interaction: Interaction):
        await self.send_message(interaction, "You do not have the privilege to do that")

    async def __sub_is_admin_function(self, interaction: Interaction, query: dict):
        existing_user = await self.db.admins.find_one(query)
        granted = existing_user is not None
        if not granted:
            await self.access_denied(interaction)

        return granted

    async def __is_admin(self, interaction: Interaction, user_id: int):
        return await self.__sub_is_admin_function(interaction, {"user_id": user_id})

    async def __is_super_admin(self, interaction: Interaction, user_id: int):
        return await self.__sub_is_admin_function(interaction, {"user_id": user_id, "super_admin": True})

    async def __update_sub_function(self, interaction: Interaction, update_function, update_params):
        try:
            logger.info(f"Attempting to update database with params: {update_params}")
            await update_function(update_params)
            await self.ack_msg(interaction)
            logger.info(f"Database updated successfully with params: {update_params}")
        except Exception as e:
            await self.error_msg(interaction, e)

    async def __check_super_admin(self, interaction: Interaction):
        user_id = interaction.user.id
        if not await self.__is_super_admin(interaction, user_id):
            logger.warning(f"User {user_id} tried to execute a privileged command without sufficient rights.")
            await self.access_denied(interaction)
            return False
        return True

    async def __update_status_sub_function(self, interaction: Interaction, user_id: int, update_function, update_params,
                                           not_found_message="User already listed"):
        existing_user = await self.db.admins.find_one({"user_id": user_id})
        if existing_user:
            logger.info(f"Updating user {user_id} with params: {update_params}")
            await update_function(*update_params)
            await self.ack_msg(interaction)
            logger.info(f"User {user_id} updated successfully.")
        else:
            logger.info(f"User {user_id} not found for update operation.")
            await self.not_found(interaction, not_found_message)

    @app_commands.command(name="grant", description="Grant admin rights to a user")
    async def grant(self, interaction: Interaction, user_id: int):
        logger.info(f"Grant command invoked by {interaction.user.id} for user {user_id}.")
        if not await self.__check_super_admin(interaction):
            return

        existing_user = await self.db.admins.find_one({"user_id": user_id})
        if not existing_user:
            await self.__update_sub_function(interaction, self.db.admins.insert_one,
                                             {"user_id": user_id, "super_admin": False})
            logger.info(f"Granted admin rights to user {user_id}.")
        else:
            await self.duplicate(interaction)
            logger.info(f"Grant command failed: User {user_id} is already listed.")

    @app_commands.command(name="upgrade", description="Upgrade a user to super admin")
    async def upgrade(self, interaction: Interaction, user_id: int):
        logger.info(f"Upgrade command invoked by {interaction.user.id} for user {user_id}.")
        if not await self.__check_super_admin(interaction):
            return

        await self.__update_status_sub_function(interaction, user_id, self.db.admins.update_one,
                                                ({"user_id": user_id}, {"$set": {"super_admin": True}}),
                                                "User is not admin. Grant rights before upgrading")
        logger.info(f"Upgraded user {user_id} to super admin.")

    @app_commands.command(name="downgrade", description="Downgrade a user from super admin to regular admin")
    async def downgrade(self, interaction: Interaction, user_id: int):
        logger.info(f"Downgrade command invoked by {interaction.user.id} for user {user_id}.")
        if not await self.__check_super_admin(interaction):
            return

        await self.__update_status_sub_function(interaction, user_id, self.db.admins.update_one,
                                                ({"user_id": user_id}, {"$set": {"super_admin": False}}))
        logger.info(f"Downgraded user {user_id} from super admin to regular admin.")

    @app_commands.command(name="revoke", description="Revoke admin rights from a user")
    async def revoke(self, interaction: Interaction, user_id: int):
        logger.info(f"Revoke command invoked by {interaction.user.id} for user {user_id}.")
        if not await self.__check_super_admin(interaction):
            return

        await self.__update_status_sub_function(interaction, user_id, self.db.admins.delete_one,
                                                ({"user_id": user_id},))
        logger.info(f"Revoked admin rights from user {user_id}.")

    @app_commands.command(name="super_admin", description="Create a super admin if none exists")
    async def super_admin(self, interaction: Interaction, user_id: int):
        logger.info(f"Super admin command invoked by {interaction.user.id} for user {user_id}.")
        existing_super_admin = await self.db.admins.find_one({"super_admin": True})
        if existing_super_admin:
            logger.info(f"Super admin already defined. Command invoked by {interaction.user.id}.")
            await self.send_message(interaction, "Super admin already defined")
        else:
            await self.__update_sub_function(interaction, self.db.admins.insert_one,
                                             {"user_id": user_id, "super_admin": True})
            logger.info(f"Created new super admin with user ID {user_id}.")

# To add this Cog to your bot, you'll use:
# bot.add_cog(AdminManagementCog(bot, db))
