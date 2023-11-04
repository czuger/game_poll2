import logging

import discord
from discord.ext import commands

import libs.database as database
from libs.poll import Poll
from libs.poll_embedding import get_players_embed
from libs.poll_view import PollView


# Configuration de la connexion MongoDB


class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True  # This is a privileged intent, must be enabled in the portal too.
        intents.message_content = True  # This enables the "Message Content" intent

        super().__init__(command_prefix="g2!", intents=intents)

    async def setup_hook(self) -> None:
        async def message_refresh_function(poll_key):
            __poll = await Poll.find(database.db, poll_key)
            pv = PollView(__poll)

        for _poll in database.polls_collection.find():
            await message_refresh_function(_poll["key"])

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


database.initialize_db()
bot = PersistentViewBot()


@bot.command()
async def poll(ctx):
    _poll = await Poll.find_or_create(database.db, ctx.channel)
    pv = PollView(_poll)

    embed = await get_players_embed(database.db, ctx.channel)

    await ctx.send("Activités", embed=embed, view=pv)


# @bot.event
# async def on_message(message):
#     print(message.channel.id, message.content)

with open("discord_token.txt", 'r') as f:
    bot.run(f.read(), log_level=logging.DEBUG)
