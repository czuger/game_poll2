import time

from poll.libs.objects.database import DbConnector
from poll.libs.objects.guild import Guild
from poll.libs.interfaces.helpers.replace_spaces_and_non_ansi import replace_spaces_and_non_ansi


class GameAlreadyExist(RuntimeError):
    pass


async def add_temporary_game(guild: Guild, db: DbConnector, game_name: str):
    new_game_key = replace_spaces_and_non_ansi(game_name)
    game_dict = {
        "key": new_game_key,
        "long": game_name,
        "short": game_name,
        "temporary": True,
        "add_timestamp": time.time()
    }
    game = await db.guilds.find_one({"key": guild.key}, {f"games.{new_game_key}": 1})
    if game and new_game_key in game.get('games', {}):
        raise GameAlreadyExist

    await db.guilds.update_one({"key": guild.key}, {"$set": {f"games.{new_game_key}": game_dict}})
