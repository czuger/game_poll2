from discord.ext.commands import Context

from libs.dat.database import DbConnector
from libs.dat.guild import Guild
from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed
from libs.poll.poll_view import PollView


# Configuration de la connexion MongoDB


async def __show_poll(ctx: Context, db: DbConnector, poll: Poll):
    pv = PollView()

    await pv.initialize_view(db, poll)
    embed = await get_players_embed(db, ctx.channel)
    await ctx.send("", embed=embed, view=pv)


# TODO : merge those two functions
async def __show_poll_by_channel(channel, db: DbConnector, poll: Poll):
    pv = PollView()

    await pv.initialize_view(db, poll)
    embed = await get_players_embed(db, channel)
    await channel.send("", embed=embed, view=pv)


async def command_poll(ctx: Context, db: DbConnector):
    poll = await Poll.find(db, ctx.channel, create_if_not_exist=True)
    await __show_poll(ctx, db, poll)


async def reset_poll_cmd(ctx: Context, db: DbConnector):
    # if await is_admin(db, ctx.interaction, ctx.me.id):
    poll = await Poll.find(db, ctx.channel)
    await poll.remove_poll_from_db()
    poll = await Poll.find(db, ctx.channel, create_if_not_exist=True)
    await __show_poll(ctx, db, poll)


async def reset_guild_cmd(ctx: Context, db: DbConnector):
    # if await is_admin(db, ctx.interaction, ctx.me.id):
    guild = await Guild.find_or_create(db, ctx.channel)
    await guild.remove_poll_from_db()
    await Guild.find_or_create(db, ctx.channel)
