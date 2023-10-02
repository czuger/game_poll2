import logging
import pprint
import json
import discord
from discord.ext import commands
from pymongo import MongoClient

from libs.poll_manager import PollManager

# Configuration de la connexion MongoDB

with open("mongo.json", "r") as f:
    mongo = json.load(f)

client = MongoClient('rpi4fe', 27017, username=mongo["user"], password=mongo["pass"])
db = client["games_database"]
games_collection = db["games"]
polls_collection = db["poll_instance"]

pm = PollManager(client)
pp = pprint.PrettyPrinter(indent=4)


# My button class is a call for when someone presses a button
class PollButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        pm.toggle_vote(interaction.channel, interaction.user, self.custom_id)

        embed = pm.get_players_embed(interaction.channel)
        print(embed)
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)


class OtherButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        pm.toggle_others(interaction.channel, interaction.user, self.custom_id)

        embed = pm.get_players_embed(interaction.channel)
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)


class PollView(discord.ui.View):
    def __custom_id(self, label):
        return f"{label}"

    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

        key = OtherButton(label="Clés", custom_id=self.__custom_id("pkey"), emoji='🔑',
                          style=discord.ButtonStyle.success, row=0)
        self.add_item(key)

        key = OtherButton(label="Tournoi", custom_id=self.__custom_id("tournament"), emoji='🏅',
                          style=discord.ButtonStyle.danger, row=0)
        self.add_item(key)

        self.games = [game["name"] for game in games_collection.find()]
        self.games.sort()

        if not self.games:
            print("No self.games")

        for game in self.games:
            button = PollButton(label=game, custom_id=self.__custom_id(game), row=1)
            self.add_item(button)

        # key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)

        key = OtherButton(label="Autre", custom_id=self.__custom_id("other"), emoji='♟️',
                          style=discord.ButtonStyle.success, row=2)
        # action_row = discord.ActionRow(key)
        self.add_item(key)

        # key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)

    # async def interaction_check(self, interaction: discord.Interaction):
    #     """Vérifie que l'interaction provient du bon canal."""
    #     print("interaction.channel.id == self.channel_id", interaction.channel.id, self.channel_id)
    #     return interaction.channel.id == self.channel_id


class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True  # This is a privileged intent, must be enabled in the portal too.
        intents.message_content = True  # This enables the "Message Content" intent

        super().__init__(command_prefix="g2!", intents=intents)

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        async def message_refresh_function(channel_id, message_id):
            print("Add view for channel", channel_id)
            print("Add view for message", message_id)

            pv = PollView(channel_id)

            print("Poll view = ", pv)
            print(pv)

            for c in pv.children:
                print(c)
                print(c.custom_id)
                print(c.callback)
            print(self.add_view(pv, message_id=message_id))
            # https://github.com/Rapptz/discord.py/blob/master/examples/views/persistent.py
            # https://stackoverflow.com/questions/76748561/discord-py-button-persistency-confusion
            # https://stackoverflow.com/questions/65789837/dicord-py-get-channel-returns-none

            print(pv)

        await pm.refresh_poll_messages(message_refresh_function)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = PersistentViewBot()


@bot.command()
async def create(ctx):
    """Crée un sondage basé sur les jeux de la collection 'games'."""
    poll = polls_collection.find_one({"channel_id": str(ctx.channel.id)})
    if not poll:
        # buttons = [discord.ui.Button(style=1, label=game, custom_id=game) for game in games]
        view = PollView(ctx.channel.id)
        # TODO : use https://discordpy.readthedocs.io/en/stable/api.html?highlight=embed#discord.Embed instead of text
        # ctx.send(embed=embed, view=view)
        embed = pm.get_players_embed(ctx.channel)
        poll_message = await ctx.send("Activités", embed=embed, view=view)

        new_poll = {
            "guild_id": str(ctx.channel.guild.id),
            "channel_id": str(ctx.channel.id),
            "message_id": str(poll_message.id),
            "games": view.games,
            "choices": {},
            "others": {}
        }
        polls_collection.insert_one(new_poll)


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
