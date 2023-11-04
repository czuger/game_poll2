import discord

import libs.database as database
from libs.poll import Poll
from libs.poll_embedding import get_players_embed


class PollButton(discord.ui.Button):
    def __init__(self, db, poll: Poll, label: str, custom_id: str, row: int, emoji=None, style=discord.ButtonStyle.gray):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        self.poll = poll
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        self.poll.toggle_button_id(interaction.user, self.custom_id)

        embed = await get_players_embed(self.db, interaction.channel)

        poll_message = interaction.message
        await poll_message.edit(embed=embed)

        await interaction.response.defer(thinking=False)
