import datetime
import json
from dataclasses import field
from typing import Tuple

from beanie import Document, Indexed

from poll.misc.project_root import find_project_root

default_games = None
games_cache = {}


async def __get_pre_loaded_games() -> Tuple[dict, list]:
    """
    Asynchronously retrieves the keys of default games from the database.

    Parameters
    ----------

    Returns
    -------
    list
        A dict of miniatures, board and default games.
    """
    root_directory = find_project_root()

    with open(root_directory / "games" / "games.json") as f:
        result = json.load(f)
        return result["games"], result["poll_default"]


async def check_games_at_startup() -> None:
    global default_games

    games, default_games = await __get_pre_loaded_games()

    for game in games.values():
        if not await GameOrmObject.find_one(GameOrmObject.key == game["key"]):
            new_game = GameOrmObject(key=game["key"], long=game["long"], short=game["short"], game_type=game["type"])
            await new_game.insert()


class GameOrmObject(Document):
    key: Indexed(str, unique=True)
    short: str
    long: str
    game_type: str

    temporary: bool = False
    add_date: datetime.datetime = field(default_factory=lambda: datetime.datetime.now())

    class Settings:
        name = "games"


async def get_game(game_key: str) -> GameOrmObject:
    global games_cache

    game = games_cache.get(game_key, None)

    if not game:
        game = await GameOrmObject.find_one(GameOrmObject.key == game_key)
        if not game:
            raise RuntimeError(f"{game_key} is not in game database")
        games_cache[game_key] = game

    return game


async def get_game_short(game_key: str) -> str:
    game = await get_game(game_key)
    return game.short


async def get_game_long(game_key: str) -> str:
    game = await get_game(game_key)
    return game.long
