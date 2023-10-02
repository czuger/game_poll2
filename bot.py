import discord
from discord.ext import commands
from pymongo import MongoClient

intents = discord.Intents.default()  # This will enable all non-privileged intents
intents.members = True  # This is a privileged intent, must be enabled in the portal too.
intents.message_content = True  # This enables the "Message Content" intent

bot = commands.Bot(command_prefix="g2!", intents=intents)

# Configuration de la connexion MongoDB
client = MongoClient('localhost', 27017, username='root', password='example')
db = client["games_database"]
games_collection = db["games"]
polls_collection = db["poll_instance"]

key_emoji = None

# My button class is a call for when someone presses a button
class PollButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        # Setting vars for the class.

        game_voted = self.custom_id  # This retrieves the game name
        user_id = interaction.user.id

        poll = polls_collection.find_one({"channel_id": str(interaction.channel.id)})
        print(poll)

        if not poll:
            await interaction.response.send_message("Erreur lors du vote.")
            return

        # Check if user has already voted for this game
        if str(user_id) in poll["votes"] and poll["votes"][str(user_id)] == game_voted:
            # Remove the vote
            poll["votes"].pop(str(user_id))
            response_msg = f"Votre vote pour {game_voted} a été retiré."
        else:
            # Register or update the vote
            poll["votes"][str(user_id)] = game_voted
            response_msg = f"Vous avez voté pour {game_voted}!"

        polls_collection.update_one({"channel_id": str(interaction.channel.id)}, {"$set": {"votes": poll["votes"]}})
        await interaction.response.send_message(response_msg)


class OtherButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        # Setting vars for the class.

        game_voted = self.custom_id

        response_msg = f"Vous avez cliqué sur {game_voted}!"
        await interaction.response.send_message(response_msg)


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

        key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # action_row = discord.ActionRow(key)
        self.add_item(key)

        key = OtherButton(label="Autre", custom_id="other", emoji='♟️', style=discord.ButtonStyle.success, row=2)
        # action_row = discord.ActionRow(key)
        self.add_item(key)

        key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # action_row = discord.ActionRow(key)
        self.add_item(key)

    async def interaction_check(self, interaction: discord.Interaction):
        """Vérifie que l'interaction provient du bon canal."""
        print(f"{interaction.channel.id} == {self.channel_id}")
        return interaction.channel.id == self.channel_id

@bot.command()
async def create(ctx):
    global key_emoji

    """Crée un sondage basé sur les jeux de la collection 'games'."""
    games = [game["name"] for game in games_collection.find()]

    key_emoji = discord.utils.get(ctx.guild.emojis, name='key')
    if not games:
        await ctx.send("Aucun jeu n'est disponible pour créer un sondage.")
        return

    new_poll = {
        "channel_id": str(ctx.channel.id),
        "games": games,
        "votes": {}
    }
    polls_collection.insert_one(new_poll)

    # buttons = [discord.ui.Button(style=1, label=game, custom_id=game) for game in games]
    view = PollView(games, ctx.channel.id)
    await ctx.send(f"Sondage créé pour les jeux: {', '.join(games)}", view=view)


@bot.command()
async def show(ctx):
    """Affiche le sondage actuel pour le canal avec des boutons pour voter."""
    poll = polls_collection.find_one({"channel_id": str(ctx.channel.id)})

    if not poll:
        await ctx.send("Aucun sondage n'a été créé pour ce canal.")
        return

    games = poll["games"]

    view = PollView(games, ctx.channel.id)
    await ctx.send("Votez pour votre jeu préféré :", view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


with open("discord_token.txt", 'r') as f:
    bot.run(f.read())
