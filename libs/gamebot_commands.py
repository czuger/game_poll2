from discord.ext.commands import Context

from libs.admin import is_admin
from libs.database import DbConnector
from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed
from libs.poll.poll_view import PollView


# Configuration de la connexion MongoDB


async def __show_poll(ctx: Context, db: DbConnector, poll: Poll):
    pv = PollView()

    await pv.initialize_view(db, poll)
    embed = await get_players_embed(db, ctx.channel)
    await ctx.send("", embed=embed, view=pv)


async def command_poll(ctx: Context, db: DbConnector):
    poll = await Poll.find_or_create(db, ctx.channel)
    await __show_poll(ctx, db, poll)


async def reset_command(ctx: Context, db: DbConnector):
    if is_admin(db, ctx.interaction, ctx.me.id):
        poll = await Poll.find_or_create(db, ctx.channel)

        poll.polls.update_one({"key": poll.key}, {"$set": {poll.SELECTIONS_KEY: {}}})

        await __show_poll(ctx, db, poll)
