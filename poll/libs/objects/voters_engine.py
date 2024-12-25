import logging
from typing import Optional

import discord

from poll.libs.misc.constants import KEY
from poll.libs.misc.logging.set_logging import VOTERS_ENGINE_LOG_NAME
from poll.libs.objects.guild import Guild
from poll.libs.objects.poll import Poll

# Configure the logger for the voters engine
logger = logging.getLogger(VOTERS_ENGINE_LOG_NAME)


class VotersEngine:
    """
    A class to manage voting functionalities for a poll.

    Attributes:
        poll (Poll): An instance of the Poll class representing the current poll.
        poll_instances (collection): A database collection for poll instances.
        poll_key (str): The unique key for the poll instance.
    """

    def __init__(self, poll: Poll):
        """
        Initialize the VotersEngine with a given Poll instance.

        Args:
            poll (Poll): The poll instance to manage votes for.
        """
        self.poll = poll
        self.poll_instances = self.poll.db.poll_instances
        self.poll_key = self.poll.key

    async def reset_votes(self):
        """
        Reset all votes for the current poll by clearing the votes field in the database.
        """
        await self.poll_instances.update_one(
            {"key": self.poll_key},
            {'$set': {'votes': {}}}
        )

    async def __button_id_to_element_key(self, button_id: str) -> Optional[str]:
        """
        Find a button in the poll's button groups (games or others) using its ID.

        Args:
            button_id (str): The ID of the button to search for.

        Returns:
            dict: The database entry containing the button details, or None if not found.
        """
        if button_id in self.poll.games:
            return self.poll.games[button_id]["key"]
        elif button_id in self.poll.others:
            return self.poll.others[button_id]["key"]
        else:
            logger.error(f"For poll {self.poll_key}, button {button_id} not found in "
                         f"{self.poll.games}, {self.poll.others}")


        return None

    async def toggle_vote(self, user: discord.User, button_id: str):
        """
        Toggle a user's vote for a button in the poll.

        Args:
            user (discord.User): The user toggling the vote.
            button_id (str): The ID of the button being voted on.

        Logs:
            Debugging information about the button and voting operation.
            Critical log if the button is not found in the poll.
        """
        user_key = str(user.id)
        logger.debug(f"For poll {self.poll_key}, toggle_button_call {button_id} by {user_key}")

        # Find the button in the poll
        element_key = await self.__button_id_to_element_key(button_id)

        if element_key:
            # Retrieve or create the guild associated with the poll's channel
            guild = await Guild.find_or_create(self.poll.db, self.poll.channel)

            logger.debug(f"For poll {self.poll_key}, element_key = {element_key}")

            # Check if the user has already voted for the element
            votes_for_key = self.poll.votes.get(element_key)
            game_voted = user_key in (votes_for_key or [])
            logger.debug(f"For poll {self.poll_key}, game_voted = {game_voted}")

            # Toggle the vote by either removing or adding the user's vote
            if game_voted:
                update_result = await self.poll_instances.update_one(
                    {'key': self.poll_key}, {'$pull': {f'votes.{element_key}': user_key}}
                )
                await guild.un_count_vote(element_key, user_key)
            else:
                update_result = await self.poll_instances.update_one(
                    {'key': self.poll_key}, {'$push': {f'votes.{element_key}': user_key}}
                )
                await guild.count_vote(element_key, user_key)

            # Log the result of the update operation
            if update_result.modified_count > 0:
                logger.debug(f'{user_key} {button_id} modification done for poll {self.poll_key} success.')
            else:
                logger.debug(f'{user_key} {button_id} modification done for poll {self.poll_key} failed.')
                logger.debug(f'{update_result}')

    def get_votes(self):
        """
        Retrieve and organize the votes for the current poll.

        Returns:
            dict: A dictionary mapping poll options (games and others) to their voters.
        """
        votes = {Poll.GAMES_KEY: {}, Poll.OTHERS_KEY: {}}
        for other in self.poll.others.values():
            logger.debug(f"For poll {self.poll.key}, other = {other}")
            voters = self.poll.votes.get(other["key"], [])
            votes[Poll.OTHERS_KEY][other[KEY]] = voters

        for game in self.poll.games.values():
            logger.debug(f"For poll {self.poll.key}, game = {game}")
            voters = self.poll.votes.get(game["key"], [])
            votes[Poll.GAMES_KEY][game[KEY]] = voters

        return votes
