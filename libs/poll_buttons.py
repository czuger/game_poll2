import discord

from libs.poll import Poll
import libs.database as database
from libs.poll_embedding import get_players_embed


class PollButton(discord.ui.Button):
    def __init__(self, poll: Poll, label: str, custom_id: str, row: int, emoji=None, style=discord.ButtonStyle.gray):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        self.poll = poll

    async def callback(self, interaction: discord.Interaction):
        self.poll.toggle_button_id(interaction.user, self.custom_id)
        # pm.toggle_vote(interaction.channel, interaction.user, self.custom_id)
        #
        embed = await get_players_embed(database.db, interaction.channel)
        # print(embed)
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)
