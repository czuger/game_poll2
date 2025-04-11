import logging

import discord

from poll.interfaces.add_game.add_game_to_poll.add_game_to_poll import add_game_to_poll
from poll.interfaces.poll.helpers.build_buttons_list import PollButtonElement
from poll.interfaces.poll.poll_view import PollView
from poll.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.misc.params_bundle import ParamsBundle
from poll.orm.game_orm_object import get_game_long
from poll.orm.redis import get_button_associated_key

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


class AddToPollButton(discord.ui.Button):
    """
    This the response to the add button in the AddGame view.
    """

    def __init__(self, params_b: ParamsBundle, button_element: PollButtonElement):
        super().__init__(label=button_element.short_str, custom_id=button_element.key, row=button_element.row)
        self.params_b = params_b

    async def callback(self, interaction: discord.Interaction):

        logger.debug(f"In callback : {self.label}, {self.custom_id}")

        game_key = await get_button_associated_key(self.params_b.redis_connection, self.custom_id)
        logger.debug(f"In AddToPollButton : game_key = {game_key}")

        (self.params_b, was_added) = await add_game_to_poll(self.params_b, game_key)
        long_name = await get_game_long(game_key)

        if was_added:
            # Were we able to add the game ?
            pv = PollView()

            await pv.initialize_view(self.params_b)
            await self.params_b.add_game_button_interaction.message.edit(view=pv)

            await interaction.response.send_message(f"{long_name} a bien été ajouté.", delete_after=30,
                                                    ephemeral=True)
        else:
            # The game was already in database.
            await interaction.response.send_message(f"{long_name} est déjà présent.", delete_after=30,
                                                    ephemeral=True)
