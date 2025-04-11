import logging

import discord

from poll.interfaces.add_game.add_to_poll_button import AddToPollButton
from poll.interfaces.poll.helpers.build_buttons_list import build_poll_button_element
from poll.interfaces.poll.helpers.sort_and_split import sort_and_split
from poll.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.misc.params_bundle import ParamsBundle
from poll.orm.poll_orm_object import ButtonType

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


class AddToPollView(discord.ui.View):
    """
    This is the view(s) produced by the AddGame button.
    """

    def __init__(self):
        """
        Initializes the PollView class with no timeout.
        """
        super().__init__(timeout=None)

    async def initialize_view(self, params_b: ParamsBundle, remaining_games_chunks: list) -> "AddToPollView":
        """
        Create the view for the poll (buttons + embedded text)

        Returns
        -------
        PollView
            The initialized PollView instance.
        """

        in_rows_games = sort_and_split(remaining_games_chunks, chunk_size=5)
        for row_index, row in enumerate(in_rows_games):
            for game_key in row:
                button_element = await build_poll_button_element(params_b, ButtonType.GAME, game_key,
                                                                 row_index)
                button = AddToPollButton(params_b, button_element)
                logger.debug(f"In AddToPollView.initialize_view, adding button {button}")
                self.add_item(button)

        return self
