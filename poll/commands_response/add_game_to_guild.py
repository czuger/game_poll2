import datetime
from typing import Tuple

from poll.misc.params_bundle import ParamsBundle
from poll.misc.replace_spaces_and_non_ansi import replace_spaces_and_non_ansi
from poll.orm.game_orm_object import GameOrmObject


class GameAlreadyExist(RuntimeError):
    pass


async def add_game_to_guild(params_b: ParamsBundle, game_name: str) -> Tuple[ParamsBundle, bool]:
    new_game_key = replace_spaces_and_non_ansi(game_name)

    game = await GameOrmObject.find_one(GameOrmObject.key == new_game_key)
    if not game:
        new_game = GameOrmObject(key=new_game_key, long=game_name, short=game_name, temporary=True,
                                 add_date=datetime.datetime.now(), game_type="undefined")

        await new_game.save()

    if new_game_key not in params_b.guild.games:
        params_b.guild.games.append(new_game_key)

        return params_b, True

    return params_b, False
