import logging

import discord

from libs.add_game.add_game_to_poll_view import AddToPollView
from libs.dat.guild import Guild
from libs.helpers.views import sort_and_split_by_chunks
from libs.misc.set_logging import ADD_GAMES_LOG_NAME
from libs.poll.poll import Poll

logger = logging.getLogger(ADD_GAMES_LOG_NAME)

add_game_waiting_user = {}


class RespondToAddGameButton(discord.ui.Button):
    """
    This class create the button that is used to react to the "Add new game" button in the main poll
    """

    def __init__(self, db, poll: Poll, label: str, custom_id: str, row: int, emoji=None,
                 style=discord.ButtonStyle.gray):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        logger.debug(f"In RespondToAddGameButton.init, custom_id={custom_id}")
        self.poll = poll
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        logger.debug("In RespondToAddGameButton")

        await interaction.response.send_message("La suite se passe en discussion privée 😎", delete_after=30,
                                                ephemeral=True)

        guild = await Guild.find_or_create(self.db, interaction.channel)

        games_keys = list(guild.games.keys())
        logger.debug(f"In RespondToAddGameButton, games_keys = {games_keys}")
        for v in self.poll.games.values():
            k = v["key"]
            if k in games_keys:
                games_keys.remove(v["key"])

        logger.debug(f"In RespondToAddGameButton, cleaned games_keys = {games_keys}")

        chunks = sort_and_split_by_chunks(games_keys, guild)
        for index, chunk in enumerate(chunks):
            pv = AddToPollView()
            await pv.initialize_view(self.db, guild, self.poll, interaction.message, chunk)

            await interaction.user.send(f"Quel jeu voulez vous ajouter ? ({index})", view=pv, delete_after=300)

        # await interaction.user.send(f"Pour ajouter un jeu qui n'est pas dans a liste, tapez son nom",
        #                             delete_after=10)
