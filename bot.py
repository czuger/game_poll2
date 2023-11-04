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
        # pv = PollView(None)
        # self.add_view(pv, message_id=None)
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        async def message_refresh_function(poll_key):
            __poll = await Poll.find(database.db, poll_key)
            pv = PollView(__poll)

            print(self.add_view(pv))
            # https://github.com/Rapptz/discord.py/blob/master/examples/views/persistent.py
            # https://stackoverflow.com/questions/76748561/discord-py-button-persistency-confusion
            # https://stackoverflow.com/questions/65789837/dicord-py-get-channel-returns-none

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


# """Crée un sondage basé sur les jeux de la collection 'games'."""
# poll = polls_collection.find_one({"channel_id": str(ctx.channel.id)})
# if not poll:
#     # buttons = [discord.ui.Button(style=1, label=game, custom_id=game) for game in games]
#     view = PollView(ctx.channel.id)
#     # TODO : use https://discordpy.readthedocs.io/en/stable/api.html?highlight=embed#discord.Embed instead of text
#     # ctx.send(embed=embed, view=view)
#     embed = pm.get_players_embed(ctx.channel)
#     poll_message = await ctx.send("Activités", embed=embed, view=view)
#     ctx.channel.guild.
#     new_poll = {
#         "guild_id": str(ctx.channel.guild.id),
#         "channel_id": str(ctx.channel.id),
#         "message_id": str(poll_message.id),
#         "games": view.games,
#         "choices": {},
#         "others": {}
#     }
#     polls_collection.insert_one(new_poll)


# @bot.command()
# async def show(ctx):
#     """Affiche le sondage actuel pour le canal avec des boutons pour voter."""
#     poll = polls_collection.find_one({"channel_id": str(ctx.channel.id)})
#
#     if not poll:
#         await ctx.send("Aucun sondage n'a été créé pour ce canal.")
#         return
#
#     games = poll["games"]
#
#     view = PollView(games, ctx.channel.id)
#     await ctx.send("Votez pour votre jeu préféré :", view=view)


with open("discord_token.txt", 'r') as f:
    bot.run(f.read(), log_level=logging.DEBUG)
