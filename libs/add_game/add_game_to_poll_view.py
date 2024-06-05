import discord

from libs.add_game.add_to_poll_button import AddToPollButton
from libs.dat.guild import Guild
from libs.helpers.buttons import make_btn_key
from libs.poll.poll import Poll


class AddToPollView(discord.ui.View):
    """
    A class used to represent the poll view in a Discord UI, containing interactive buttons.

    Methods
    -------
    __init__()
        Initializes the PollView class with no timeout.
    initialize_view(db, poll)
        Asynchronously initializes the view by adding poll buttons to the view.
    """

    def __init__(self):
        """
        Initializes the PollView class with no timeout.
        """
        super().__init__(timeout=None)

    async def initialize_view(self, db, guild: Guild, poll: Poll, poll_message, chunk):
        """
        Create the view for the poll (buttons + embedded text)

        Parameters
        ----------
        db : pymongo.database.Database
            The database object.
        poll : Poll
            An instance of the Poll class representing the current poll.

        Returns
        -------
        PollView
            The initialized PollView instance.
        """
        games_db_object = chunk

        games = []

        # We create two lists. One for games, one for buttons (because buttons are in a separated line)
        for game_in in games_db_object:
            game = {"short": game_in["short"],
                    "key": make_btn_key(game_in["key"], 'g'),
                    "style": discord.ButtonStyle.primary}
            games.append(game)

        # We need to rearrange buttons in packets of 5
        packet_size = 5
        packets = [games[i:i + packet_size] for i in range(0, len(games), packet_size)]

        # We create the poll buttons for selectable games
        row = 0
        for packet in packets:
            for game in packet:
                button = AddToPollButton(db, guild, poll, poll_message, game["short"], game["key"], row)
                self.add_item(button)
            row += 1

            if row >= 4:
                break

        return self
