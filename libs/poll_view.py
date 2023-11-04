import logging
import pprint
import json
import discord
from discord.ext import commands
from pymongo import MongoClient

from libs.poll_manager import PollManager
from libs.poll_buttons import PollButton
from libs.poll_buttons import OtherButton


class PollView(discord.ui.View):
    def __custom_id(self, label):
        return f"{label}"

    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

        key = OtherButton(label="Clés", custom_id=self.__custom_id("pkey"), emoji='🔑',
                          style=discord.ButtonStyle.success, row=0)
        self.add_item(key)

        key = OtherButton(label="Tournoi", custom_id=self.__custom_id("tournament"), emoji='🏅',
                          style=discord.ButtonStyle.danger, row=0)
        self.add_item(key)

        self.games = [game["name"] for game in games_collection.find()]
        self.games.sort()

        if not self.games:
            print("No self.games")

        for game in self.games:
            button = PollButton(label=game, custom_id=self.__custom_id(game), row=1)
            self.add_item(button)

        # key = OtherButton(label="Plateau", custom_id="board", emoji='👑', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)

        key = OtherButton(label="Autre", custom_id=self.__custom_id("other"), emoji='♟️',
                          style=discord.ButtonStyle.success, row=2)
        # action_row = discord.ActionRow(key)
        self.add_item(key)

        # key = OtherButton(label="Ajouter", custom_id="add", emoji='➕', style=discord.ButtonStyle.success, row=2)
        # # action_row = discord.ActionRow(key)
        # self.add_item(key)
