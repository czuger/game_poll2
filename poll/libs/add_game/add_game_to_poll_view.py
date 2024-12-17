import json
import logging
from copy import copy

import discord

from poll.libs.add_game.add_to_poll_button import AddToPollButton
from poll.libs.dat.guild import Guild
from poll.libs.helpers.buttons import make_btn_key
from poll.libs.misc.set_logging import ADD_GAMES_LOG_NAME
from poll.libs.poll.poll import Poll

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


class AddToPollView(discord.ui.View):
    """
    A class used to represent the poll view in a Discord UI, containing interactive buttons.

    Methods
    -------
    __init__()
        Initializes the PollView class with no timeout.
    initialize_view(db, poll)
        Asynchronously initializes the view by adding poll buttons to the view.
    """

    def __init__(self):
        """
        Initializes the PollView class with no timeout.
        """
        super().__init__(timeout=None)

    async def initialize_view(self, db, guild: Guild, poll: Poll, poll_message, chunk):
        """
        Create the view for the poll (buttons + embedded text)

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        poll : Poll
            An instance of the Poll class representing the current poll.

        Returns
        -------
        PollView
            The initialized PollView instance.
        """
        games_db_object = chunk

        games = []

        for game_key in games_db_object:
            logger.debug(f"In AddToPollView.initialize_view, game_key = {game_key}")
            game_in = copy(guild.games[game_key])
            game = {"short": game_in["short"],
                    "key": make_btn_key(game_in["key"], 'g'),
                    "style": discord.ButtonStyle.primary}
            games.append(game)

        shorts = [item["short"] for item in games]
        logger.debug(f"In AddToPollView.initialize_view, games before packets = {shorts}")

        # We need to rearrange buttons in packets of 5
        packet_size = 5
        packets = [games[i:i + packet_size] for i in range(0, len(games), packet_size)]

        shorts_nested = [[item["short"] for item in sublist] for sublist in packets]
        pretty_shorts_nested = json.dumps(shorts_nested, indent=4)
        logger.debug(f"In AddToPollView.initialize_view, in packets = "
                     f"{pretty_shorts_nested}")

        # We create the poll buttons for selectable games
        row = 0
        for packet in packets:
            for game in packet:
                button = AddToPollButton(db, guild, poll, poll_message, game["short"], game["key"], row)
                logger.debug(f"In AddToPollView.initialize_view, adding button {button}")
                self.add_item(button)
            row += 1

            logger.debug(f"In AddToPollView.initialize_view, row = {row}")

            if row >= 5:
                break

        return self
