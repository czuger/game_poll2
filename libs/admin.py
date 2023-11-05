import logging

DELETE_TIME = 15
logger = logging.getLogger(__name__)


async def send_message(interaction, content):
    await interaction.response.send_message(content=content, ephemeral=True, delete_after=DELETE_TIME)


async def ack_msg(interaction):
    await send_message(interaction, "Done")


async def error_msg(interaction, exception):
    logger.error(exception)
    await send_message(interaction, "Error happened during operation")


async def duplicate(interaction):
    await send_message(interaction, "User already listed")


async def not_not_found(interaction):
    await send_message(interaction, "User is not admin")


async def access_denied(interaction):
    await send_message(interaction, "You do not have the privilege to do that")


async def __sub_is_admin_function(db, interaction, query):
    existing_user = db.admins.find_one(query)
    granted = existing_user is not None
    if not granted:
        await access_denied(interaction)

    return granted


async def is_admin(db, interaction, user_id):
    return await __sub_is_admin_function({"user_id": user_id})


async def is_super_admin(db, interaction, user_id):
    return await __sub_is_admin_function({"user_id": user_id, "super_admin": True})


async def grant(db, interaction, user_id):
    existing_user = db.admins.find_one({"user_id": user_id})
    if not existing_user:
        user_data = {"user_id": user_id, "super_admin": False}

        try:
            db.admins.insert_one(user_data)
            await ack_msg(interaction)
        except Exception as e:
            await error_msg(interaction, e)
    else:
        await duplicate(interaction)


async def upgrade(db, interaction, user_id):
    existing_user = db.admins.find_one({"user_id": user_id})
    if existing_user:
        db.admins.update_one({"user_id": user_id}, {"$set": {"super_admin": True}})
        await ack_msg(interaction)
    else:
        await interaction.response.send_message(content="User is not admin. Grant rights before upgrading",
                                                ephemeral=True, delete_after=DELETE_TIME)


async def downgrade(db, interaction, user_id):
    existing_user = db.admins.find_one({"user_id": user_id})
    if existing_user:
        db.admins.update_one({"user_id": user_id}, {"$set": {"super_admin": False}})
        await ack_msg(interaction)
    else:
        await not_not_found(interaction)


async def revoke(db, interaction, user_id):
    existing_user = db.admins.find_one({"user_id": user_id})
    if existing_user:
        db.admins.delete_one({"user_id": user_id})
        await ack_msg(interaction)
    else:
        await not_not_found(interaction)
