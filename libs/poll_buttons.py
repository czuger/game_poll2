import logging
import pprint
import json
import discord
from discord.ext import commands
from pymongo import MongoClient

from libs.poll_manager import PollManager


class PollButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        pm.toggle_vote(interaction.channel, interaction.user, self.custom_id)

        embed = pm.get_players_embed(interaction.channel)
        print(embed)
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)


class OtherButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        pm.toggle_others(interaction.channel, interaction.user, self.custom_id)

        embed = pm.get_players_embed(interaction.channel)
        poll_message = interaction.message
        await poll_message.edit(embed=embed)
        await interaction.response.send_message(content="Done", ephemeral=True, delete_after=1)

