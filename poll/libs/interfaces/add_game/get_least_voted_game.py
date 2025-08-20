import datetime
import logging

from poll.libs.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


def find_lowest_voted_game(guild: Guild, poll: Poll):
    lowest_score = 999999999
    lowest_key = None
    lowest_poll_key = None

    logger.info(f"In find_lowest_voted_game poll = {poll}")

    for game_poll_key in poll.games.keys():
        game_key = poll.games[game_poll_key]["key"]
        one_year_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=365)
        add_date = poll.games[game_poll_key].get("add_date", one_year_ago)

        if add_date.tzinfo is None:
            add_date = add_date.replace(tzinfo=datetime.UTC)
            
        if add_date > datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1):
            continue
            # We skip games added recently.

        score = guild.games[game_key].get("votes_score", 0)

        logger.info(f"Game score = {game_key}, {score}")

        if score < lowest_score:
            lowest_score = score
            lowest_key = game_key
            lowest_poll_key = game_poll_key

    logger.info(f"Lowest key = {lowest_poll_key}, {lowest_key}, {lowest_score}")
    return lowest_poll_key


def trim_games_list(guild: Guild, poll: Poll):
    """We will remove all games over 19 to make room to the new one"""
    logger.info(f"len(poll.games) = {len(poll.games)}")
    while len(poll.games) >= 20:
        logger.info(f"len(poll.games) = {len(poll.games)}")

        least_game_key = find_lowest_voted_game(guild, poll)
        logger.info(f"least_game_key = {least_game_key}")

        logger.info(f"poll.games.keys() - before = {poll.games.keys()}")
        del poll.games[least_game_key]
        logger.info(f"poll.games.keys() - after = {poll.games.keys()}")

    return poll
