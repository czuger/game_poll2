import logging

from discord.ext import commands

from poll.libs.dat.database import DbConnector
from poll.libs.misc.set_logging import ADMINS_LOG_NAME

DELETE_TIME = 15
logger = logging.getLogger(ADMINS_LOG_NAME)


async def send_message(ctx: commands.Context, content: str):
    await ctx.send(content=content, ephemeral=True, delete_after=DELETE_TIME)


async def ack_msg(ctx: commands.Context):
    await send_message(ctx, "Done")


async def error_msg(ctx: commands.Context, exception: Exception):
    logger.error(f"Error during operation: {exception}")
    await send_message(ctx, "Error happened during operation")


async def duplicate(ctx: commands.Context):
    await send_message(ctx, "User already listed")


async def not_found(ctx: commands.Context, message="User is not admin"):
    await send_message(ctx, message)


async def access_denied(ctx: commands.Context):
    author_id = ctx.author.id
    author_name = ctx.author.name
    logger.warning(f"Access denied for : {author_id} ({author_name})")
    await send_message(ctx, "You do not have the privilege to do that")


async def update_sub_function(ctx: commands.Context, update_function, update_params):
    try:
        logger.info(f"Attempting to update database with params: {update_params}")
        await update_function(update_params)
        await ack_msg(ctx)
        logger.info(f"Database updated successfully with params: {update_params}")
    except Exception as e:
        await error_msg(ctx, e)


async def __sub_is_admin_function(db: DbConnector, ctx: commands.Context, query: dict):
    existing_user = await db.admins.find_one(query)
    granted = existing_user is not None
    if not granted:
        await access_denied(ctx)

    return granted


async def is_admin(db: DbConnector, ctx: commands.Context, user_id: int):
    logger.info(f"Admin check for user : {user_id}")
    return await __sub_is_admin_function(db, ctx, {"user_id": user_id})


async def is_super_admin(db: DbConnector, ctx: commands.Context, user_id: int):
    logger.info(f"Super admin check for user : {user_id}")
    return await __sub_is_admin_function(db, ctx, {"user_id": user_id, "super_admin": True})


async def update_status_sub_function(db: DbConnector, ctx: commands.Context, user_id: int, update_function,
                                     update_params,
                                     not_found_message="User already listed"):
    existing_user = await db.admins.find_one({"user_id": user_id})
    if existing_user:
        logger.info(f"Updating user {user_id} with params: {update_params}")
        await update_function(*update_params)
        await ack_msg(ctx)
        logger.info(f"User {user_id} updated successfully.")
    else:
        logger.info(f"User {user_id} not found for update operation.")
        await not_found(ctx, not_found_message)


async def check_super_admin(db: DbConnector, ctx: commands.Context):
    user_id = ctx.author.id
    if not await is_super_admin(db, ctx, user_id):
        logger.warning(f"User {user_id} tried to execute a privileged command without sufficient rights.")
        await access_denied(ctx)
        return False
    return True


async def grant(db: DbConnector, ctx: commands.Context, user_id: int):
    logger.info(f"Grant command invoked by {ctx.author.id} for user {user_id}.")
    if not await check_super_admin(db, ctx):
        return

    existing_user = await db.admins.find_one({"user_id": user_id})
    if not existing_user:
        await update_sub_function(ctx, db.admins.insert_one,
                                  {"user_id": user_id, "super_admin": False})
        logger.info(f"Granted admin rights to user {user_id}.")
    else:
        await duplicate(ctx)
        logger.info(f"Grant command failed: User {user_id} is already listed.")


async def upgrade(db: DbConnector, ctx: commands.Context, user_id: int):
    logger.info(f"Upgrade command invoked by {ctx.author.id} for user {user_id}.")
    if not await check_super_admin(db, ctx):
        return

    await update_status_sub_function(db, ctx, user_id, db.admins.update_one,
                                     ({"user_id": user_id}, {"$set": {"super_admin": True}}),
                                     "User is not admin. Grant rights before upgrading")
    logger.info(f"Upgraded user {user_id} to super admin.")


async def downgrade(db: DbConnector, ctx: commands.Context, user_id: int):
    logger.info(f"Downgrade command invoked by {ctx.author.id} for user {user_id}.")
    if not await check_super_admin(db, ctx):
        return

    await update_status_sub_function(
        db, ctx, user_id, db.admins.update_one, ({"user_id": user_id}, {"$set": {"super_admin": False}}))
    logger.info(f"Downgraded user {user_id} from super admin to regular admin.")


async def revoke(db: DbConnector, ctx: commands.Context, user_id: int):
    logger.info(f"Revoke command invoked by {ctx.author.id} for user {user_id}.")
    if not await check_super_admin(db, ctx):
        return

    await update_status_sub_function(db, ctx, user_id, db.admins.delete_one, ({"user_id": user_id},))
    logger.info(f"Revoked admin rights from user {user_id}.")


async def super_admin(db: DbConnector, ctx: commands.Context):
    """Set the caller as super admin. Can be called only once."""
    user_id = ctx.author.id
    logger.info(f"Super admin command invoked by {user_id} for user {user_id}.")
    existing_super_admin = await db.admins.find_one({"super_admin": True})
    if existing_super_admin:
        logger.info(f"Super admin already defined. Command invoked by {user_id}.")
        await send_message(ctx, "Super admin already defined")
    else:
        logger.info(f"Created new super admin with user ID {user_id}.")
        await update_sub_function(ctx, db.admins.insert_one, {"user_id": user_id, "super_admin": True})
        await send_message(ctx, "You are super admin")
