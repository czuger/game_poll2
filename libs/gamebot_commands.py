from discord.ext.commands import Context

from libs.dat.database import DbConnector
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
    poll = await Poll.find(db, ctx.channel, create_if_not_exist=True)
    await __show_poll(ctx, db, poll)


async def reset_command(ctx: Context, db: DbConnector):
    # if await is_admin(db, ctx.interaction, ctx.me.id):
    poll = await Poll.find(db, ctx.channel, create_if_not_exist=True)
    print(poll.buttons)
    new_buttons = await poll.add_default_games(ctx.channel)
    poll.buttons = new_buttons
    print(poll.buttons)
    await __show_poll(ctx, db, poll)
