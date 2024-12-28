from poll.libs.objects.poll.poll_games import PollGames


class PollVotes(PollGames):
    async def reset_votes(self):
        """
        Reset all votes for the current poll by clearing the votes field in the database.
        """
        await self.poll_instances.update_one(
            {"key": self.poll_key},
            {'$set': {'votes': {}}}
        )

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
        element_key = self.poll.button_id_to_element_key(button_id)

        if element_key:
            # Retrieve or create the guild associated with the poll's channel
            guild = await Guild.find_or_create_by_channel(self.poll.db, self.poll.channel)

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

    def get_votes(self) -> dict:
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

    def get_votes_for_element(self, element_key: str) -> dict:
        """
        Retrieve and organize the votes for the current poll.

        Returns:
            dict: A dictionary mapping poll options (games and others) to their voters.
        """

        if element_key not in self.poll.votes:
            raise ElementNotInVotesDict(element_key, self.poll.votes)

        return self.poll.votes[element_key]
