from typing import Tuple

from poll.interfaces.add_game.add_game_to_poll.select_game_to_remove import select_game_to_remove
from poll.misc.objects import ButtonType
from poll.misc.params_bundle import ParamsBundle
from poll.orm.poll_orm_object import PollElement


def make_room_for_new_game(params_b: ParamsBundle) -> ParamsBundle:
    game_key_to_remove = select_game_to_remove(params_b)
    del params_b.poll.poll_elements[game_key_to_remove]

    return params_b


async def add_game_to_poll(params_b: ParamsBundle, game_key: str) -> Tuple[ParamsBundle, bool]:
    if game_key not in params_b.poll.poll_elements:
        if len(params_b.poll.poll_elements.keys()) >= 20:
            params_b = make_room_for_new_game(params_b)

        params_b.poll.poll_elements[game_key] = PollElement(object_key=game_key, object_type=ButtonType.GAME)

        await params_b.poll.save()

        return params_b, True
    else:
        return params_b, False
