import logging

import discord

from poll.interfaces.add_game.add_game_to_poll_view import AddToPollView
from poll.interfaces.poll.helpers.build_poll_button_element import PollButtonElement
from poll.interfaces.poll.helpers.sort_and_split import sort_and_split
from poll.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.misc.params_bundle import ParamsBundle

logger = logging.getLogger(ADD_GAMES_LOG_NAME)

add_game_waiting_user = {}


class RespondToAddGameButton(discord.ui.Button):
    """
    This class is used to respond to the AddGame button in the poll.
    """

    def __init__(self, params_b: ParamsBundle, poll_button_element: PollButtonElement):
        super().__init__(label=poll_button_element.short_str, custom_id=poll_button_element.key,
                         emoji=poll_button_element.emoji, style=discord.ButtonStyle(str(poll_button_element.style)),
                         row=poll_button_element.row)
        logger.debug(f"In RespondToAddGameButton.init, custom_id={poll_button_element.custom_id}")
        self.params_b = params_b

    async def callback(self, interaction: discord.Interaction):
        logger.debug("In RespondToAddGameButton")

        await interaction.response.send_message("La suite se passe en discussion privée 😎", delete_after=30,
                                                ephemeral=True)

        remaining_games = list(set(self.params_b.guild.games) - set(self.params_b.poll.poll_elements))
        logger.debug(
            f"In RespondToAddGameButton, guild.games = {self.params_b.guild.games}, "
            f"poll_selected_games = {self.params_b.poll.poll_elements}, "
            f"remaining_games = {remaining_games}")

        remaining_games_chunks = sort_and_split(remaining_games)

        self.params_b.add_game_button_interaction = interaction
        for index, chunk in enumerate(remaining_games_chunks):
            pv = AddToPollView()
            await pv.initialize_view(self.params_b, chunk)

            await interaction.user.send(f"Quel jeu voulez vous ajouter ? ({index})", view=pv, delete_after=300)

        # await interaction.user.send(f"Pour ajouter un jeu qui n'est pas dans a liste, tapez son nom",
        #                             delete_after=10)
