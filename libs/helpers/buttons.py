import random


def make_btn_key(game_key: str, typ: str):
    """
    Creates a unique button key.

    Parameters
    ----------
    game_key : str
        The key of the game.
    typ : str
        The type of button (e.g., "G" for game, "O" for other).

    Returns
    -------
    str
        A unique button key.
    """
    tmp_gk = game_key[5:-1] if typ == "G" else game_key
    return "BTN" + typ + "_" + tmp_gk + "_" + format(random.randrange(0, 10 ** 9), '09d')
