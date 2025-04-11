import logging

import discord
import redis
from discord import Message

from poll.interfaces.add_game.add_to_poll_button import AddToPollButton
from poll.interfaces.helpers.sort_and_split import sort_and_split
from poll.libs.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.orm.guild_orm_object import GuildOrmObject
from poll.orm.helpers.polls.rebuild_buttons import build_poll_button_element
from poll.orm.poll_orm_object import PollOrmObject, ButtonType

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

    async def initialize_view(self, redis_connection: redis.Redis, guild: GuildOrmObject, poll: PollOrmObject,
                              poll_message: Message, remaining_games_chunks: list) -> "AddToPollView":
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
                button_element = await build_poll_button_element(redis_connection, ButtonType.GAME, game_key, row_index)
                button = AddToPollButton(guild, poll, poll_message, button_element)
                logger.debug(f"In AddToPollView.initialize_view, adding button {button}")
                self.add_item(button)

        return self
