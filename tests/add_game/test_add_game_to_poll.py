import unittest
from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase

from poll.interfaces.add_game.add_game_to_poll.add_game_to_poll import add_game_to_poll
from poll.orm.helpers.polls.votes import add_vote, remove_vote
from tests.base import BotTest, get_games_keys_not_in_poll


class TestAddToPollButton(IsolatedAsyncioTestCase, unittest.TestCase, BotTest):

    async def asyncSetUp(self):
        await self.set_up()

    async def test_add_game_to_poll_new_game_should_be_added(self):
        self.assertTrue(await add_game_to_poll(self.params_b, "adg"))

    async def test_add_game_to_poll_new_game_should_be_added_and_least_voted_should_be_removed(self):
        remaining_games_keys = await get_games_keys_not_in_poll(self.params_b)

        # We fill
        for i in range(15):
            key = str(remaining_games_keys.pop())
            await add_game_to_poll(self.params_b, key)

        for key in self.params_b.poll.poll_elements:
            self.params_b = await add_vote(self.params_b, key, 1)

        # Testing remove votes by the way
        self.params_b = await remove_vote(self.params_b, "adg", 1)

        key = str(remaining_games_keys.pop())
        await add_game_to_poll(self.params_b, key)

        # After adding a new game, ADG should be removed as it is the least voted.
        self.assertNotIn("adg", self.params_b.poll.poll_elements)

    async def test_add_game_to_poll_new_game_should_be_added_and_older_voted_should_be_removed(self):
        remaining_games_keys = await get_games_keys_not_in_poll(self.params_b)

        # We fill
        for i in range(15):
            key = str(remaining_games_keys.pop())
            await add_game_to_poll(self.params_b, key)

        for key in self.params_b.poll.poll_elements:
            self.params_b = await add_vote(self.params_b, key, 1)

        self.guild.total_votes_data["saga"].last_vote = datetime.now() - timedelta(days=10000)

        key = str(remaining_games_keys.pop())
        await add_game_to_poll(self.params_b, key)

        # After adding a new game, SAGA should be removed as it is the least voted.
        self.assertNotIn("saga", self.params_b.poll.poll_elements)
