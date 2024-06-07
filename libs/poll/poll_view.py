import discord

from libs.add_game.respond_to_add_game_button import RespondToAddGameButton
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
        await poll.refresh()

        # We need to rearrange buttons in packets of 5
        packet_size = 5
        keys = list(poll.games.keys())
        packets_keys = [keys[i:i + packet_size] for i in range(0, len(keys), packet_size)]

        # We create the poll buttons for selectable games
        row = 0
        for packet_keys in packets_keys:
            for key in packet_keys:
                game = poll.games[key]
                button = PollButton(db, poll, game["short"], key, row)
                self.add_item(button)
            row += 1

        # We create the buttons for other actions
        for key, other in poll.others.items():
            if "action" in other:
                if "add_game" in other["action"]:
                    button = RespondToAddGameButton(
                        db, poll, other["short"], key, row, emoji=other["emoji"], style=other["style"])
                    print("Adding 'add_game' button : ", key, button)
                else:
                    raise RuntimeError(f"Unknown action : {other['action']}")
            else:
                button = PollButton(db, poll, other["short"], key, row, emoji=other["emoji"], style=other["style"])
            self.add_item(button)

        return self
