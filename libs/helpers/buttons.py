import random
import re


def make_btn_key(game_key: str, btn_typ: str):
    """
    Creates a unique button key.

    Parameters
    ----------
    game_key : str
        The key of the game.

    Returns
    -------
    str
        A unique button key.
    """
    return btn_typ + "_" + game_key + "_" + format(random.randrange(0, 10 ** 9), '09d')


def get_key_from_btn(btn_key: str):
    match = re.search(r'[gmbo]_(.+)_\d+', btn_key)
    if match:
        return match.group(1)
    return None
