import discord

from libs.poll import Poll
from libs.poll_buttons import PollButton


class PollView(discord.ui.View):

    def __init__(self, poll: Poll):
        super().__init__(timeout=None)

        games = [(v["short"], k, discord.ButtonStyle.primary) for k, v in poll.games.items()]
        games.sort()

        packet_size = 5
        packets = [games[i:i + packet_size] for i in range(0, len(games), packet_size)]

        row = 0
        for packet in packets:
            for game in packet:
                (short, key, style) = game
                button = PollButton(poll, short, key, row)
                self.add_item(button)

            row += 1

        for k, v in poll.others.items():
            button = PollButton(poll, v["short"], k, row, emoji=v["emoji"], style=discord.ButtonStyle.primary)
            self.add_item(button)

        # key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)

        # key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)
