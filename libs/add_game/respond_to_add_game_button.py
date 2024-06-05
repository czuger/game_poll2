import discord

from libs.add_game.add_game_to_poll_view import AddToPollView
from libs.dat.games import Games
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
        games = await Games.get_games(self.db)

        print("Got games")

        miniatures_dict = games.get_miniatures_dict()
        chunks = sort_and_split_by_chunks(miniatures_dict)
        for index, chunk in enumerate(chunks):
            pv = AddToPollView()
            await pv.initialize_view(self.db, self.poll, chunk)

            await interaction.user.send(f"Quel jeu de figurines voulez vous ajouter ? ({index})", view=pv)

        board_dict = games.get_board_games_dict()
        chunks = sort_and_split_by_chunks(board_dict)
        for index, chunk in enumerate(chunks):
            pv = AddToPollView()
            await pv.initialize_view(self.db, self.poll, chunk)

            await interaction.user.send(f"Quel jeu de plateau voulez vous ajouter ? ({index})", view=pv)
