import logging

import discord

from poll.libs.interfaces.helpers.buttons import get_key_from_btn
from poll.libs.misc.logging.set_logging import ADD_GAMES_LOG_NAME
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll

logger = logging.getLogger(ADD_GAMES_LOG_NAME)


class AddToPollButton(discord.ui.Button):
    """
    This class create a button that will add a game in the poll
    """

    def __init__(self, db, guild: Guild, poll: Poll, poll_message, label: str, custom_id: str, row: int):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.db = db
        self.poll = poll
        self.guild = guild
        self.poll_message = poll_message

    async def callback(self, interaction: discord.Interaction):
        from poll.libs.poll.poll_view import PollView

        logger.debug(f"In callback : {self.label}, {self.custom_id}")

        game_key = get_key_from_btn(self.custom_id)
        logger.debug(f"In AddToPollButton : game_key = {game_key}")

        (was_added, long_name) = await self.poll.add_game(game_key)
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
