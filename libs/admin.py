import logging

from discord.interactions import Interaction

from libs.database import DbConnector

DELETE_TIME = 15
logger = logging.getLogger(__name__)


async def send_message(interaction: Interaction, content):
    await interaction.response.send_message(content=content, ephemeral=True, delete_after=DELETE_TIME)


async def ack_msg(interaction: Interaction):
    await send_message(interaction, "Done")


async def error_msg(interaction: Interaction, exception):
    logger.error(exception)
    await send_message(interaction, "Error happened during operation")


async def duplicate(interaction: Interaction):
    await send_message(interaction, "User already listed")


async def not_not_found(interaction: Interaction, message="User is not admin"):
    await send_message(interaction, message)


async def access_denied(interaction: Interaction):
    await send_message(interaction, "You do not have the privilege to do that")


async def __sub_is_admin_function(db: DbConnector, interaction: Interaction, query):
    existing_user = await db.admins.find_one(query)
    granted = existing_user is not None
    if not granted:
        await access_denied(interaction)

    return granted


async def is_admin(db: DbConnector, interaction: Interaction, user_id: int):
    return await __sub_is_admin_function(db, interaction, {"user_id": user_id})


async def is_super_admin(db: DbConnector, interaction: Interaction, user_id: int):
    return await __sub_is_admin_function(db, interaction, {"user_id": user_id, "super_admin": True})


async def __update_sub_function(interaction: Interaction, update_function, update_params):
    try:
        await update_function(update_params)
        await ack_msg(interaction)
    except Exception as e:
        await error_msg(interaction, e)


async def grant(db: DbConnector, interaction: Interaction, user_id: int):
    existing_user = await db.admins.find_one({"user_id": user_id})
    if not existing_user:
        await __update_sub_function(interaction, db.admins.insert_one, {"user_id": user_id, "super_admin": False})
    else:
        await duplicate(interaction)


async def __update_status_sub_function(db: DbConnector, interaction: Interaction, user_id: int, update_function,
                                       update_params,
                                       not_found_message="User already listed"):
    existing_user = db.admins.find_one({"user_id": user_id})
    if existing_user:
        await update_function(*update_params)
        await ack_msg(interaction)
    else:
        await not_not_found(interaction, not_found_message)


async def upgrade(db: DbConnector, interaction: Interaction, user_id: int):
    await __update_status_sub_function(db, interaction, user_id, db.admins.update_one,
                                       ({"user_id": user_id}, {"$set": {"super_admin": True}}),
                                       "User is not admin. Grant rights before upgrading")


async def downgrade(db: DbConnector, interaction: Interaction, user_id: int):
    await __update_status_sub_function(db, interaction, user_id, db.admins.update_one,
                                       ({"user_id": user_id}, {"$set": {"super_admin": False}}))


async def revoke(db: DbConnector, interaction, user_id: int):
    await __update_status_sub_function(db, interaction, user_id, db.admins.delete_one, ({"user_id": user_id},))
