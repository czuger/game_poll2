import logging

import discord

from poll.interfaces.add_game.add_game_to_poll_view import AddToPollView
from poll.interfaces.helpers.sort_and_split import sort_and_split
from poll.libs.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.orm.guild_orm_object import get_guild
from poll.orm.poll_orm_object import PollOrmObject

logger = logging.getLogger(ADD_GAMES_LOG_NAME)

add_game_waiting_user = {}


class RespondToAddGameButton(discord.ui.Button):
    """
    This class is used to respond to the AddGame button in the poll.
    """

    def __init__(self, poll: PollOrmObject, label: str, custom_id: str, row: int, emoji=None,
                 style=discord.ButtonStyle.gray):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        logger.debug(f"In RespondToAddGameButton.init, custom_id={custom_id}")
        self.poll = poll

    async def callback(self, interaction: discord.Interaction):
        logger.debug("In RespondToAddGameButton")

        await interaction.response.send_message("La suite se passe en discussion privée 😎", delete_after=30,
                                                ephemeral=True)

        guild = await get_guild(interaction.channel.guild.id)

        remaining_games = list(set(guild.games) - set(self.poll.selected_games))
        logger.debug(
            f"In RespondToAddGameButton, guild.games = {guild.games}, poll_selected_games = {self.poll.selected_games}, "
            f"remaining_games = {remaining_games}")

        remaining_games_chunks = sort_and_split(remaining_games)

        for index, chunk in enumerate(remaining_games_chunks):
            pv = AddToPollView()
            await pv.initialize_view(guild, self.poll, interaction.message, chunk)

            await interaction.user.send(f"Quel jeu voulez vous ajouter ? ({index})", view=pv, delete_after=300)

        # await interaction.user.send(f"Pour ajouter un jeu qui n'est pas dans a liste, tapez son nom",
        #                             delete_after=10)
