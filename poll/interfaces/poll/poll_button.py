import discord

from poll.interfaces.poll.helpers.build_poll_button_element import PollButtonElement
from poll.interfaces.poll.poll_embedding import get_players_embed
from poll.misc.params_bundle import ParamsBundle
from poll.orm.helpers.polls.votes import toggle_vote
from poll.orm.redis import get_button_associated_key


class PollButton(discord.ui.Button):
    """
    A class used to represent a poll button in a Discord UI.
    """

    def __init__(self, params_b: ParamsBundle, button: PollButtonElement):
        """
        Initializes the PollButton class with a database object, poll instance, and button properties.
        """

        super().__init__(label=button.short_str, custom_id=button.key, emoji=button.emoji,
                         style=discord.ButtonStyle(str(button.style)), row=button.row)
        self.params_b = params_b

    async def callback(self, interaction: discord.Interaction):
        """
        Asynchronously handles the button click interaction.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the button click event.
        """

        element_key = await get_button_associated_key(self.params_b.redis_connection, self.custom_id)

        self.params_b.poll = await toggle_vote(self.params_b.poll, element_key, interaction.user.id)
        self.params_b.interaction = interaction
        embed = await get_players_embed(self.params_b)

        # TODO : need to update all polls, not only the interaction one.
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.defer(thinking=False, ephemeral=True)
