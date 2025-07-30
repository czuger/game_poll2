import logging

from poll.libs.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


def find_lowest_voted_game(guild: Guild, poll: Poll):
    lowest_score = 999999999
    lowest_key = None

    logger.info(f"In find_lowest_voted_game poll = {poll}")

    for game_poll_key in poll.games.keys():
        game_key = poll.games[game_poll_key]["key"]
        score = guild.games[game_key].get("votes_score", 0)

        logger.info(f"Game score = {game_key}, {score}")

        if score < lowest_score:
            lowest_score = score
            lowest_key = game_key

    logger.info(f"Lowest key = {lowest_key}, {lowest_score}")
    return lowest_key
