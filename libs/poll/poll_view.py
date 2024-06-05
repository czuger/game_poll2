import discord

from libs.add_game_to_poll.respond_to_add_game_button import RespondToAddGameButton
from libs.dat.games import Games
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
        games_db_object = await Games.get_games(db)

        games = []
        others = []
        # We create two lists. One for games, one for buttons (because buttons are in a separated line)
        for button_id, button_key in poll.buttons.items():
            if button_key in poll.OTHER_BUTTONS:
                other = Poll.OTHER_BUTTONS[button_key]
                other["key"] = button_id
                others.append(other)
            else:
                game = {"short": games_db_object.dict[button_key]["short"],
                        "key": games_db_object.dict[button_key]["short"],
                        "style": discord.ButtonStyle.primary}
                games.append(game)

        # games.sort()
        # others.sort()

        # We need to rearrange buttons in packets of 5
        packet_size = 5
        packets = [games[i:i + packet_size] for i in range(0, len(games), packet_size)]

        # We create the poll buttons for selectable games
        row = 0
        for packet in packets:
            for game in packet:
                button = PollButton(db, poll, game["short"], game["key"], row)
                self.add_item(button)
            row += 1

        # We create the buttons for other actions
        for other in others:
            if "action" in other:
                if "add_game" in other["action"]:
                    button = RespondToAddGameButton(db, poll, other["short"], other["key"], row,
                                                    emoji=other["emoji"], style=other["style"])
                else:
                    raise RuntimeError(f"Unknown action : {other['action']}")
            else:
                button = PollButton(db, poll, other["short"], other["key"], row, emoji=other["emoji"],
                                    style=other["style"])
            self.add_item(button)

        # Uncomment the following lines if additional buttons are needed
        # key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # self.add_item(key)
        #
        # key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # self.add_item(key)

        return self
