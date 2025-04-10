import discord

from poll.libs.interfaces.poll.poll_embedding import get_players_embed
from poll.orm.helpers.polls.rebuild_buttons import PollButtonElement
from poll.orm.helpers.polls.votes import toggle_vote
from poll.orm.poll_orm_object import PollOrmObject


class PollButton(discord.ui.Button):
    """
    A class used to represent a poll button in a Discord UI.
    """

    def __init__(self, poll: PollOrmObject, button: PollButtonElement):
        """
        Initializes the PollButton class with a database object, poll instance, and button properties.

        Parameters
        ----------
        poll : Poll
            An instance of the Poll class associated with this button.
        """

        super().__init__(label=button.short_str, custom_id=button.key, emoji=button.emoji,
                         style=discord.ButtonStyle(str(button.style)), row=button.row)
        self.poll = poll

    async def callback(self, interaction: discord.Interaction):
        """
        Asynchronously handles the button click interaction.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the button click event.
        """

        self.poll = await toggle_vote(self.poll, self.custom_id, interaction.user.id)
        embed = await get_players_embed(self.poll, interaction.guild)

        # TODO : need to update all polls, not only the interaction one.
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.defer(thinking=False, ephemeral=True)
