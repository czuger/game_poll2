import logging

import discord
import redis
from discord import Message

from poll.interfaces.add_game.add_game_to_poll.add_game_to_poll import add_game_to_poll
from poll.interfaces.poll.poll_view import PollView
from poll.libs.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.orm.helpers.polls.rebuild_buttons import PollButtonElement
from poll.orm.poll_orm_object import PollOrmObject
from poll.orm.redis import get_button_associated_key

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


class AddToPollButton(discord.ui.Button):
    """
    This the response to the add button in the AddGame view.
    """

    def __init__(self, redis_connection: redis.Redis, poll: PollOrmObject, poll_message: Message,
                 button_element: PollButtonElement):
        super().__init__(label=button_element.short_str, custom_id=button_element.key, row=button_element.row)

        self.poll = poll
        self.poll_message = poll_message
        self.redis_connection = redis_connection

    async def callback(self, interaction: discord.Interaction):

        logger.debug(f"In callback : {self.label}, {self.custom_id}")

        game_key = await get_button_associated_key(self.redis_connection, self.custom_id)
        logger.debug(f"In AddToPollButton : game_key = {game_key}")

        (poll, guild, game_key) = await add_game_to_poll(self.poll, self.guild, game_key)
        if was_added:
            # Were we able to add the game ?
            pv = PollView()
            await pv.initialize_view(self.db, self.poll)

            await self.poll_message.edit(view=pv)
            # await interaction.user.send(f"{game['long']} a bien été ajouté.", delete_after=30)

            await interaction.response.send_message(f"{long_name} a bien été ajouté.", delete_after=30,
                                                    ephemeral=True)
        else:
            # The game was already in database.
            await interaction.response.send_message(f"{long_name} est déjà présent.", delete_after=30,
                                                    ephemeral=True)
