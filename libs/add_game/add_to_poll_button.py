from copy import copy

import discord

from libs.dat.guild import Guild
from libs.helpers.buttons import get_key_from_btn
from libs.helpers.buttons import make_btn_key
from libs.poll.poll import Poll


class AddToPollButton(discord.ui.Button):
    """
    This class create a button that will add a game in the poll
    """

    def __init__(self, db, guild: Guild, poll: Poll, poll_message, label: str, custom_id: str, row: int):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.db = db
        self.poll = poll
        self.guild = guild
        self.poll_message = poll_message

    async def callback(self, interaction: discord.Interaction):
        from libs.poll.poll_view import PollView

        print(self.label, self.custom_id)

        game_key = get_key_from_btn(self.custom_id)
        game = copy(self.guild.games[game_key])

        game["players"] = []
        new_btn_key = make_btn_key(game_key, "g")
        self.poll.games[new_btn_key] = game
        await self.db.poll_instances.update_one({"key": self.poll.key},
                                                {"$set": {f"buttons.games.{new_btn_key}": game}})

        pv = PollView()
        await pv.initialize_view(self.db, self.poll)

        await self.poll_message.edit(view=pv)
        # await interaction.user.send(f"{game['long']} a bien été ajouté.", delete_after=30)

        await interaction.response.send_message(f"{game['long']} a bien été ajouté.", delete_after=30)
