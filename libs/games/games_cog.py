from discord.ext import commands
from discord.ext.commands import Context

from libs.add_game.add_temporary_game import GameAlreadyExist
from libs.add_game.add_temporary_game import add_temporary_game
from libs.dat.database import DbConnector
from libs.dat.guild import Guild
from libs.misc.command_logger import log_command_call


class GamesCog(commands.Cog, name="jeux"):
    """All commands related to games management"""

    def __init__(self, bot, db: DbConnector):
        self.bot = bot
        self.db = db

    @commands.command(name="ajouter")
    async def add_game(self, ctx: Context, *, game_name: str):
        """Permet d'ajouter un jeu à la liste des jeux disponibles."""
        log_command_call(ctx.author, ctx.channel, "ajouter")

        game_name = game_name[0].upper() + game_name[1:]
        print(game_name)
        guild = await Guild.find_or_create(self.db, ctx.channel)

        try:
            await add_temporary_game(guild, self.db, game_name)

            await ctx.send("Le jeu a bien été ajouté.", delete_after=120)
            await ctx.send("Vous devez encore l'ajouter aux sondages avec le bouton 🧩 Ajouter", delete_after=120)

        except GameAlreadyExist:
            await ctx.send("Ce jeu existe déjà.", delete_after=120)
