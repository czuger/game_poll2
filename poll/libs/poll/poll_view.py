import logging

import discord

from poll.libs.interfaces.add_game.respond_to_add_game_button import RespondToAddGameButton
from poll.libs.misc.logging.set_logging import POLLS_LOG_NAME
from poll.libs.objects.database import DbConnector
from poll.libs.objects.poll import Poll
from poll.libs.poll.poll_buttons import PollButton

poll_logger = logging.getLogger(POLLS_LOG_NAME)


class PollView(discord.ui.View):
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

    @staticmethod
    def get_style_from_poll(other):
        return Poll.OTHER_BUTTONS[other["key"]]["style"]

    async def initialize_view(self, db: DbConnector, poll: Poll):
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
        await poll.refresh()

        keys = list(poll.games.keys())
        keys.sort(key=lambda k: poll.games[k]["short"].lower())

        grid = []
        row = []
        for i, key in enumerate(keys):
            row.append(key)

            # Start a new row after every 5 items
            if (i + 1) % 5 == 0:
                grid.append(row)
                row = []

            # Break if we've reached the maximum allowed items (5x4 = 20)
            if i + 1 >= 20:
                break

        # Add the last row if it's not empty and we haven't reached the maximum number of rows
        if row and len(grid) < 5:
            grid.append(row)

        # We create the poll buttons for selectable games
        for row_index, row in enumerate(grid):
            print(row)
            for key in row:
                button = PollButton(db, poll, poll.games[key]["short"], key, row_index)
                self.add_item(button)

        # We create the buttons for other actions
        for key, other in poll.others.items():
            poll_logger.debug(key, other)
            if "action" in other:
                if "add_game" in other["action"]:
                    button = RespondToAddGameButton(
                        db, poll, other["short"], key, row_index + 1, emoji=other["emoji"],
                        style=self.get_style_from_poll(other))
                    poll_logger.debug(f"Adding 'add_game' button : {key}, {button}, {self.get_style_from_poll(other)}")
                else:
                    raise RuntimeError(f"Unknown action : {other['action']}")
            else:
                button = PollButton(db, poll, other["short"], key, row_index + 1, emoji=other["emoji"],
                                    style=self.get_style_from_poll(other))

                poll_logger.debug(f"Adding button : {key}, {button}, {self.get_style_from_poll(other)}")
            self.add_item(button)

        return self
