import discord

from libs.games import Games
from libs.poll.poll import Poll
from libs.poll.poll_buttons import PollButton


class PollView(discord.ui.View):
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

    async def initialize_view(self, db, poll: Poll):
        """
        Asynchronously initializes the view by adding poll buttons to the view.

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
        games_db_object = await Games.get_games(db)

        games = []
        others = []
        for button_id, button_key in poll.buttons.items():
            if button_key in poll.OTHER_BUTTONS:
                others.append((Poll.OTHER_BUTTONS[button_key]["short"], button_id,
                               discord.ButtonStyle.primary, Poll.OTHER_BUTTONS[button_key]["emoji"]))
            else:
                games.append((games_db_object.dict[button_key]["short"], button_id, discord.ButtonStyle.primary))

        games.sort()
        others.sort()

        packet_size = 5
        packets = [games[i:i + packet_size] for i in range(0, len(games), packet_size)]

        row = 0
        for packet in packets:
            for game in packet:
                (short, key, style) = game
                button = PollButton(db, poll, short, key, row)
                self.add_item(button)
            row += 1

        for other in others:
            (short, key, style, emoji) = other
            button = PollButton(db, poll, short, key, row, emoji=emoji, style=style)
            self.add_item(button)

        # Uncomment the following lines if additional buttons are needed
        # key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # self.add_item(key)
        #
        # key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # self.add_item(key)

        return self
