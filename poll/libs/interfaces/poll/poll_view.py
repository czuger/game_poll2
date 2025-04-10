import logging

import discord

from poll.libs.interfaces.poll.poll_buttons import PollButton
from poll.libs.misc.logging.set_logging import POLLS_LOG_NAME
from poll.orm.poll_orm_object import PollOrmObject

poll_logger = logging.getLogger(POLLS_LOG_NAME)


class PollView(discord.ui.View):
    """
    A class used to represent the poll view in a Discord UI, containing interactive buttons.
    """

    def __init__(self):
        super().__init__(timeout=None)

    async def initialize_view(self, poll: PollOrmObject) -> "PollView":
        """
        Create the view for the poll (buttons + embedded text)

        Parameters
        ----------
        poll : Poll
            An instance of the Poll class representing the current poll.

        Returns
        -------
        PollView
            The initialized PollView instance.
        """
        for button in poll.buttons_for_view:
            button = PollButton(poll, button)
            self.add_item(button)

        return self
