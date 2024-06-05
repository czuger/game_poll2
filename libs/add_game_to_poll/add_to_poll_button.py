import discord

from libs.poll.poll import Poll


class AddToPollButton(discord.ui.Button):
    """
    This class create a button that will add a game in the poll
    """

    def __init__(self, poll: Poll, label: str, custom_id: str, row: int):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.poll = poll

    async def callback(self, interaction: discord.Interaction):
        print(self.label)

        await interaction.response.defer(thinking=False)
