import discord

from libs.add_game_to_poll.add_to_poll_view import AddToPollView
from libs.poll.poll import Poll


class RespondToAddGameButton(discord.ui.Button):
    """
    This class create the button that is used to react to the "Add new game" button in the main poll
    """

    def __init__(self, db, poll: Poll, label: str, custom_id: str, row: int, emoji=None,
                 style=discord.ButtonStyle.gray):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        self.poll = poll
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        pv = AddToPollView()

        await pv.initialize_view(self.db, self.poll)
        await interaction.user.send("Quel jeu voulez vous ajouter ?", view=pv)
