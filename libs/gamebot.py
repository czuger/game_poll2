import logging

import discord
from discord.ext import commands

from libs.database import DbConnector
from libs.poll import Poll
from libs.poll_embedding import get_players_embed
from libs.poll_view import PollView


# Configuration de la connexion MongoDB

class GameBot(commands.Bot):
    def __init__(self, db):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True  # This is a privileged intent, must be enabled in the portal too.
        intents.message_content = True  # This enables the "Message Content" intent

        super().__init__(command_prefix="g2!", intents=intents)

        self.db = db

    async def setup_hook(self) -> None:
        async def message_refresh_function(poll_key):
            refreshing_poll = await Poll.find(self.db, poll_key)
            pv = PollView()
            await pv.initialize_view(self.db, refreshing_poll)

        for to_refresh_poll in self.db.polls.find():
            await message_refresh_function(to_refresh_poll["key"])

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
