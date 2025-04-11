"""
This module mainly create the content of the poll. The part that show the status of the poll
(basically what games players have selected).
"""
import logging

import discord

from poll.interfaces.poll.helpers.get_poll_embedded_lines import get_poll_embedded_lines
from poll.misc.logging.set_logging import POLLS_LOG_NAME
from poll.misc.params_bundle import ParamsBundle
from poll.orm.helpers.polls.misc import get_players_count

logger = logging.getLogger(POLLS_LOG_NAME)


async def get_players_embed(params_b: ParamsBundle):
    """
    Create the status content of the poll.
      * Show the title
      * Show each activity / game followed with a list of user that had checked this activity / game

    Returns
    -------
    discord.Embed
        The embed object displaying the poll selections.
    """
    players_amount = f"Environs {get_players_count(params_b.poll)} joueurs prévus"
    embed = discord.Embed(title="A quoi allez vous jouer ?", color=discord.Color.blue(), description=players_amount)

    for line in await get_poll_embedded_lines(params_b):
        embed.add_field(name="", value=line, inline=False)

    return embed
