import logging

import discord
from discord.ext import commands

from libs.database import DbConnector
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
            poll = await Poll.find(db, poll_key)
            pv = PollView()
            await pv.initialize_view(db, poll)

        for poll in db.polls.find():
            await message_refresh_function(poll["key"])

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


db = DbConnector()
db.connect()
bot = PersistentViewBot()


@bot.command()
async def poll(ctx):
    poll = await Poll.find_or_create(db, ctx.channel)
    pv = PollView()
    await pv.initialize_view(db, poll)

    embed = await get_players_embed(db, ctx.channel)

    await ctx.send("Activités", embed=embed, view=pv)


# @bot.event
# async def on_message(message):
#     print(message.channel.id, message.content)

with open("discord_token.txt", 'r') as f:
    bot.run(f.read(), log_level=logging.DEBUG)
