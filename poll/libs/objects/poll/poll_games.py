import logging
from copy import copy
from typing import Optional

from discord import TextChannel

from poll.libs.interfaces.helpers.buttons import make_btn_key
from poll.libs.misc.constants import LONG_NAME
from poll.libs.misc.logging.set_logging import POLLS_LOG_NAME
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll.poll_base import PollBase

logger = logging.getLogger(POLLS_LOG_NAME)


class PollGames(PollBase):
    async def add_default_games(self, channel: TextChannel) -> None:
        """
        Asynchronously finds an existing poll in the database or creates a new one.

        Parameters
        ----------
        channel : discord.channel.Channel
            The Discord channel object from which the channel ID is extracted.

        Returns
        -------
        The new buttons keys
        """

        logger.debug("add_default_games called")
        guild = await Guild.find_or_create_by_channel(self.db, channel)

        for element_key in guild.poll_default:
            game = copy(guild.games[element_key])
            self.games[make_btn_key(element_key, "g")] = game

        for other in self.OTHER_BUTTONS.values():
            self.others[make_btn_key(other["key"], "o")] = other

        await self.db.poll_instances.update_one({"key": self.key}, {"$set": {"buttons.games": self.games}}, upsert=True)
        await self.db.poll_instances.update_one({"key": self.key}, {"$set": {"buttons.others": self.others}},
                                                upsert=True)

    async def add_game(self, game_key: str) -> (bool, Optional[str]):
        """
        Adds a game to the poll, allowing users to vote for it.

        Parameters
        ----------
        game_key : str
            The unique identifier for the game to be added to the poll.

        Returns
        -------
        tuple
            A tuple containing:
            - bool: True if the game was successfully added, False if it already exists in the poll.
            - Optional[str]: The long name of the game if added, or None if the game already exists.

        """
        if game_key not in self.get_games_keys_set():
            guild = await Guild.find(self.db, str(self.channel.guild.id))

            game = copy(guild.games[game_key])
            logger.debug(f"In Poll#add_game : game = {game}")

            new_btn_key = make_btn_key(game_key, "g")
            logger.debug(f"In Poll#add_game : new_btn_key = {new_btn_key}")

            self.games[new_btn_key] = game
            await self.db.poll_instances.update_one({"key": self.key},
                                                    {"$set": {f"buttons.games.{new_btn_key}": game}})

            return True, game[LONG_NAME]
        else:
            return False, None
