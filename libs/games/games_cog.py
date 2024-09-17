from discord.ext import commands
from discord.ext.commands import Context

from libs.add_game.add_temporary_game import GameAlreadyExist
from libs.add_game.add_temporary_game import add_temporary_game
from libs.dat.database import DbConnector
from libs.dat.guild import Guild


class GamesCog(commands.Cog, name="jeux"):
    """All commands related to games management"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajout_jeu")
    async def add_game(ctx: Context, db: DbConnector, game_name: str):
        """Permet d'ajouter un jeu à la liste des jeux disponibles."""
        game_name = game_name[0].upper() + game_name[1:]
        print(game_name)
        guild = await Guild.find_or_create(db, ctx.channel)

        try:
            await add_temporary_game(guild, db, game_name)

            await ctx.send("Le jeu a bien été ajouté.", delete_after=120)
            await ctx.send("Vous devez encore l'ajouter aux sondages avec le bouton 🧩 Ajouter", delete_after=120)

        except GameAlreadyExist:
            await ctx.send("Ce jeu existe déjà.", delete_after=120)
