import logging

import discord

from libs.misc.set_logging import COMMANDS_NAME

command_logger = logging.getLogger(COMMANDS_NAME)


def log_command_call(user: discord.User, channel: discord.TextChannel, command: str):
    command_logger.info(
        f"User: {user.name} (ID: {user.id}) issued command: {command} in channel: {channel.name} (ID: {channel.id})"
    )
