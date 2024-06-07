import discord

from libs.dat.guild import Guild
from libs.helpers.buttons import get_key_from_btn
from libs.poll.poll import Poll
from libs.poll.poll_view import PollView


class AddToPollButton(discord.ui.Button):
    """
    This class create a button that will add a game in the poll
    """

    def __init__(self, db, poll: Poll, label: str, custom_id: str, row: int):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.db = db
        self.poll = poll

    async def callback(self, interaction: discord.Interaction):
        print(self.label, self.custom_id)

        game_key = get_key_from_btn(self.custom_id)

        guild = await Guild.find_or_create(self.db, interaction.channel)

        if game_key in guild.games["miniatures"]:
            game = guild.games["miniatures"]["game_key"]
        elif game_key in guild.games["boards"]:
            game = guild.games["boards"]["game_key"]
        else:
            raise RuntimeError(f"{game_key} not found.")

        # TODO : add the game to the poll.

        poll = await Poll.find(self.db, interaction.channel)

        pv = PollView()
        await pv.initialize_view(self.db, poll)

        poll_message = interaction.message
        await poll_message.edit(view=pv)
        await interaction.response.defer(thinking=False)
