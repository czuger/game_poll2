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


async def not_not_found(interaction, message="User is not admin"):
    await send_message(interaction, )


async def access_denied(interaction):
    await send_message(interaction, "You do not have the privilege to do that")


async def __sub_is_admin_function(db, interaction, query):
    existing_user = db.admins.find_one(query)
    granted = existing_user is not None
    if not granted:
        await access_denied(interaction)

    return granted


async def is_admin(db, interaction, user_id):
    return await __sub_is_admin_function(db, interaction, {"user_id": user_id})


async def is_super_admin(db, interaction, user_id):
    return await __sub_is_admin_function(db, interaction, {"user_id": user_id, "super_admin": True})


async def __update_sub_function(interaction, update_function, update_params):
    try:
        update_function(update_params)
        await ack_msg(interaction)
    except Exception as e:
        await error_msg(interaction, e)


async def grant(db, interaction, user_id):
    existing_user = db.admins.find_one({"user_id": user_id})
    if not existing_user:
        await __update_sub_function(interaction, db.admins.insert_one, {"user_id": user_id, "super_admin": False})
    else:
        await duplicate(interaction)


async def __update_status_sub_function(db, interaction, user_id, update_function, update_params,
                                       not_found_message="User already listed"):
    existing_user = db.admins.find_one({"user_id": user_id})
    if existing_user:
        update_function(*update_params)
        await ack_msg(interaction)
    else:
        await not_not_found(interaction, not_found_message)


async def upgrade(db, interaction, user_id):
    await __update_status_sub_function(db, interaction, user_id, db.admins.update_one,
                                 ({"user_id": user_id}, {"$set": {"super_admin": True}}),
                                 "User is not admin. Grant rights before upgrading")


async def downgrade(db, interaction, user_id):
    await __update_status_sub_function(db, interaction, user_id, db.admins.update_one,
                                 ({"user_id": user_id}, {"$set": {"super_admin": False}}))


async def revoke(db, interaction, user_id):
    await __update_status_sub_function(db, interaction, user_id, db.admins.delete_one, ({"user_id": user_id},))
