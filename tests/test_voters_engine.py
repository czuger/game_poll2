import unittest
import asyncio
from unittest.mock import Mock

import discord
from poll.libs.objects.poll import Poll
from poll.libs.objects.voters_engine import VotersEngine
from tests.base import BotTest


class TestVotersEngine(unittest.IsolatedAsyncioTestCase, unittest.TestCase, BotTest):
    # TODO : connect only at class init and disconnect at class end.
    # using setUpClass and tearDownClass
    def setUp(self):
        self.set_up()

        guild = Mock(spec=discord.Guild, id="my_guild")
        self.channel = Mock(spec=discord.ChannelType, id="my_chan", guild=guild)
        self.user = Mock(spec=discord.User, id="my_user")

    async def __set_voters_engine(self):
        self.poll = await Poll.find(self.db, self.channel, create_if_not_exist=True)
        self.voters_engine = VotersEngine(self.poll)

    async def test_reset_votes(self):
        await self.__set_voters_engine()

        # Call toggle_vote to add a vote
        await self.voters_engine.toggle_vote(self.user, list(self.poll.games.keys())[0])

        # Verify the vote was added
        updated_poll = await self.db.poll_instances.find_one({"key": self.poll.key})
        self.assertIn("my_user", updated_poll["votes"]["adg"])

        # Call reset_votes
        await self.voters_engine.reset_votes()

        # Verify votes are cleared
        updated_poll = await self.db.poll_instances.find_one({"key": self.poll.key})
        self.assertEqual(updated_poll["votes"], {})

    async def test_toggle_vote_add_vote(self):
        await self.__set_voters_engine()

        # Call toggle_vote to add a vote
        await self.voters_engine.toggle_vote(self.user, list(self.poll.games.keys())[0])

        # Verify the vote was added
        updated_poll = await self.db.poll_instances.find_one({"key": self.poll.key})
        self.assertIn("my_user", updated_poll["votes"]["adg"])

    async def test_toggle_vote_remove_vote(self):
        await self.__set_voters_engine()

        game_key = list(self.poll.games.keys())[0]
        # Call toggle_vote to add a vote
        await self.voters_engine.toggle_vote(self.user, game_key)

        # Verify the vote was added
        updated_poll = await self.db.poll_instances.find_one({"key": self.poll.key})
        self.assertIn("my_user", updated_poll["votes"]["adg"])

        await self.poll.refresh()

        # Call toggle_vote to remove the vote
        await self.voters_engine.toggle_vote(self.user, game_key)

        # Verify the vote was removed
        updated_poll = await self.db.poll_instances.find_one({"key": self.poll.key})
        self.assertNotIn("my_user", updated_poll["votes"]["adg"])

    async def test_get_votes(self):
        await self.__set_voters_engine()

        game_key = list(self.poll.games.keys())[0]
        # Call toggle_vote to add a vote
        await self.voters_engine.toggle_vote(self.user, game_key)

        await self.poll.refresh()

        # Call get_votes
        votes = self.voters_engine.get_votes()

        self.assertIn("my_user", votes[Poll.GAMES_KEY]["adg"])



if __name__ == "__main__":
    unittest.main()
