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

    @staticmethod
    def get_style_from_poll(other):
        return Poll.OTHER_BUTTONS[other["key"]]["style"]

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

        packet_size = 5
        keys = list(poll.games.keys())

        # Sort keys by the length of game["short"] in descending order
        keys.sort(key=lambda k: len(poll.games[k]["short"]), reverse=True)

        # Determine the number of rows needed
        num_rows = (len(keys) + packet_size - 1) // packet_size

        # Initialize the rows, each with an empty list of games, character count, and item count
        rows = [{'games': [], 'char_count': 0, 'item_count': 0} for _ in range(num_rows)]

        # Distribute the games across rows
        for key in keys:
            game = poll.games[key]
            game_short_length = len(game["short"])

            # Find the row with the minimum character count that has less than 5 items
            min_row_index = min(
                (i for i, row in enumerate(rows) if row['item_count'] < packet_size),
                key=lambda i: rows[i]['char_count'],
                default=None
            )

            if min_row_index is not None:
                # Add the game to the selected row
                rows[min_row_index]['games'].append((key, game))
                rows[min_row_index]['char_count'] += game_short_length
                rows[min_row_index]['item_count'] += 1

        # We create the poll buttons for selectable games
        for row_index, row in enumerate(rows):
            for key, game in row['games']:
                button = PollButton(db, poll, game["short"], key, row_index)
                self.add_item(button)

        row = row_index + 1

        # We create the buttons for other actions
        for key, other in poll.others.items():
            print(key, other)
            if "action" in other:
                if "add_game" in other["action"]:
                    button = RespondToAddGameButton(
                        db, poll, other["short"], key, row, emoji=other["emoji"], style=self.get_style_from_poll(other))
                    print("Adding 'add_game' button : ", key, button, self.get_style_from_poll(other))
                else:
                    raise RuntimeError(f"Unknown action : {other['action']}")
            else:
                button = PollButton(db, poll, other["short"], key, row, emoji=other["emoji"],
                                    style=self.get_style_from_poll(other))

                print("Adding button : ", key, button, self.get_style_from_poll(other))
            self.add_item(button)

        return self
