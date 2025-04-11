import logging

import discord

from poll.interfaces.add_game.respond_to_add_game_button import RespondToAddGameButton
from poll.interfaces.poll.helpers.build_buttons_list import build_buttons_list
from poll.interfaces.poll.poll_button import PollButton
from poll.misc.logging.set_logging import POLLS_LOG_NAME
from poll.misc.params_bundle import ParamsBundle

poll_logger = logging.getLogger(POLLS_LOG_NAME)


class PollView(discord.ui.View):
    """
    A class used to represent the poll view in a Discord UI, containing interactive buttons.
    """

    def __init__(self):
        super().__init__(timeout=None)

    async def initialize_view(self, params_b: ParamsBundle) -> "PollView":
        """
        Create the view for the poll (buttons + embedded text)

        Returns
        -------
        PollView
            The initialized PollView instance.
        """
        for button_element in await build_buttons_list(params_b):
            if button_element.key == "add":
                button = RespondToAddGameButton(params_b, button_element)
            else:
                button = PollButton(params_b, button_element)

            self.add_item(button)

        return self
