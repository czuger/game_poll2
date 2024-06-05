from copy import copy

import discord

from libs.add_game.add_game_to_poll_view import AddToPollView
from libs.dat.guild import Guild
from libs.helpers.views import sort_and_split_by_chunks
from libs.poll.poll import Poll


class RespondToAddGameButton(discord.ui.Button):
    """
    This class create the button that is used to react to the "Add new game" button in the main poll
    """

    def __init__(self, db, poll: Poll, label: str, custom_id: str, row: int, emoji=None,
                 style=discord.ButtonStyle.gray):
        super().__init__(label=label, custom_id=custom_id, emoji=emoji, style=style, row=row)
        print(custom_id)
        self.poll = poll
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        print("In RespondToAddGameButton")
        guild = await Guild.find_or_create(self.db, interaction.channel)

        miniatures = copy(guild.games["miniatures"])
        for v in self.poll.games.values():
            if v["key"] in miniatures:
                del miniatures[v["key"]]

        chunks = sort_and_split_by_chunks(miniatures)
        for index, chunk in enumerate(chunks):
            pv = AddToPollView()
            await pv.initialize_view(self.db, guild, self.poll, interaction.message, chunk)

            await interaction.user.send(f"Quel jeu de figurines voulez vous ajouter ? ({index})", view=pv)

        boards = copy(guild.games["boards"])
        for v in self.poll.games.values():
            if v["key"] in boards:
                del boards[v["key"]]

        chunks = sort_and_split_by_chunks(boards)
        for index, chunk in enumerate(chunks):
            pv = AddToPollView()
            await pv.initialize_view(self.db, guild, self.poll, interaction.message, chunk)

            await interaction.user.send(f"Quel jeu de plateau voulez vous ajouter ? ({index})", view=pv)
