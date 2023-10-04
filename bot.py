import discord
from discord.ext import commands
from pymongo import MongoClient
from libs.poll_manager import PollManager
from libs.poll_manager import register_poll_message
from libs.poll_manager import get_poll_message

intents = discord.Intents.default()  # This will enable all non-privileged intents
intents.members = True  # This is a privileged intent, must be enabled in the portal too.
intents.message_content = True  # This enables the "Message Content" intent

bot = commands.Bot(command_prefix="g2!", intents=intents)

# Configuration de la connexion MongoDB
client = MongoClient('localhost', 27017, username='root', password='example')
db = client["games_database"]
games_collection = db["games"]
polls_collection = db["poll_instance"]

pm = PollManager(client)


# My button class is a call for when someone presses a button
class PollButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        pm.toggle_vote(interaction.channel, interaction.user, self.custom_id)

        message = pm.get_players_string(interaction.channel)
        poll_message = get_poll_message(interaction.channel)
        await poll_message.edit(content=message)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)


class OtherButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        pm.toggle_others(interaction.channel, interaction.user, self.custom_id)

        message = pm.get_players_string(interaction.channel)
        poll_message = get_poll_message(interaction.channel)
        await poll_message.edit(content=message)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)


class PollView(discord.ui.View):
    def __init__(self, games, channel_id):
        super().__init__()
        self.channel_id = channel_id

        key = OtherButton(label="Clés", custom_id="pkey", emoji='🔑', style=discord.ButtonStyle.success, row=0)
        self.add_item(key)

        key = OtherButton(label="Tournoi", custom_id="tournament", emoji='🏅', style=discord.ButtonStyle.danger, row=0)
        self.add_item(key)

        for game in games:
            button = PollButton(label=game, custom_id=game, row=1)
            self.add_item(button)

        # key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)

        key = OtherButton(label="Autre", custom_id="other", emoji='♟️', style=discord.ButtonStyle.success, row=2)
        # action_row = discord.ActionRow(key)
        self.add_item(key)

        # key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)

    async def interaction_check(self, interaction: discord.Interaction):
        """Vérifie que l'interaction provient du bon canal."""
        return interaction.channel.id == self.channel_id


@bot.command()
async def create(ctx):
    """Crée un sondage basé sur les jeux de la collection 'games'."""
    games = [game["name"] for game in games_collection.find()]
    games.sort()

    if not games:
        await ctx.send("Aucun jeu n'est disponible pour créer un sondage.")
        return

    poll = polls_collection.find_one({"channel_id": str(ctx.channel.id)})
    if not poll:
        new_poll = {
            "channel_id": str(ctx.channel.id),
            "games": games,
            "choices": {},
            "others": {}
        }
        polls_collection.insert_one(new_poll)

    # buttons = [discord.ui.Button(style=1, label=game, custom_id=game) for game in games]
    view = PollView(games, ctx.channel.id)
    # TODO : use https://discordpy.readthedocs.io/en/stable/api.html?highlight=embed#discord.Embed instead of text
    # ctx.send(embed=embed, view=view)
    message = pm.get_players_string(ctx.channel)
    poll_message = await ctx.send(message, view=view)
    register_poll_message(ctx.channel, poll_message)


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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


with open("discord_token.txt", 'r') as f:
    bot.run(f.read())
