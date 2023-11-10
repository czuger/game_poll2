import discord

from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed


class AddToPollButton(discord.ui.Button):
    def __init__(self, poll: Poll, label: str, custom_id: str, row: int):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.poll = poll

    async def callback(self, interaction: discord.Interaction):
        self.poll.toggle_button_id(interaction.user, self.custom_id)

        embed = await get_players_embed(self.db, interaction.channel)

        poll_message = interaction.message
        await poll_message.edit(embed=embed)

        await interaction.response.defer(thinking=False)
