import discord

from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed


class PollButton(discord.ui.Button):
    """
    A class used to represent a poll button in a Discord UI.

    Attributes
    ----------
    poll : Poll
        An instance of the Poll class associated with this button.
    db : pymongo.database.Database
        The database object.

    Methods
    -------
    __init__(self, db, poll, label, custom_id, row, emoji=None, style=discord.ButtonStyle.gray)
        Initializes the PollButton class with a database object, poll instance, and button properties.
    callback(self, interaction)
        Asynchronously handles the button click interaction.
    """

    def __init__(self, db, poll: Poll, label: str, custom_id: str, row: int, emoji=None,
                 style=discord.ButtonStyle.gray):
        """
        Initializes the PollButton class with a database object, poll instance, and button properties.

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        poll : Poll
            An instance of the Poll class associated with this button.
        label : str
            The label text for the button.
        custom_id : str
            The custom ID for the button.
        row : int
            The row in which the button is placed.
        emoji : Optional[discord.Emoji], optional
            The emoji to display on the button (default is None).
        style : discord.ButtonStyle, optional
            The style of the button (default is discord.ButtonStyle.gray).
        """
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        self.poll = poll
        self.db = db

        print("Creating button", label, custom_id)

    async def callback(self, interaction: discord.Interaction):
        """
        Asynchronously handles the button click interaction.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the button click event.
        """
        await self.poll.toggle_button_id(interaction.user, self.custom_id)
        embed = await get_players_embed(self.db, interaction.channel)
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.defer(thinking=False)
