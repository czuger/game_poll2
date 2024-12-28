import logging

import discord

from poll.libs.misc.constants import KEY
from poll.libs.misc.logging.set_logging import POLLS_LOG_NAME
from poll.libs.objects.database import DbConnector
from poll.libs.objects.poll.poll_votes import PollVotes

basic_methods = __import__("0_basic_methods")

logger = logging.getLogger(POLLS_LOG_NAME)


class ButtonIdNotInPoll(RuntimeError):
    """
    Exception raised when a button id is not found in the poll other or games dictionaries.
    """

    def __init__(self, button_id: str, games: dict):
        message = f"{button_id} not found in {games}"
        super().__init__(message)


class Poll(PollVotes):
    """
    A class used to represent and manage polls in a MongoDB collection.
    """

    OTHER_BUTTONS = {
        "present_with_key": {"key": "present_with_key", "short": "Clés", "long": "Présent avec les clés", "emoji": "🔑",
                             "style": discord.ButtonStyle.green},
        # "tournament_orga": {"key": "tournament_orga", "short": "Tournoi/Orga",
        #                     "long": "En tournoi ou en orga de tournoi", "emoji": "🍺",
        #                     "style": discord.ButtonStyle.success},
        "other": {"key": "other", "short": "Autre", "long": "Autre activité", "emoji": "♟️",
                  "style": discord.ButtonStyle.blurple},
        "away": {"key": "away", "short": "Absent", "long": "Absent", "emoji": "⛱️",
                 "style": discord.ButtonStyle.blurple},
        "add": {"key": "add", "short": "Ajouter", "long": "Ajouter un jeu", "emoji": "🧩",
                "style": discord.ButtonStyle.grey, "action": "add_game"},
    }

    BUTTONS_KEY = "buttons"
    GAMES_KEY = "games"
    OTHERS_KEY = "others"
    VOTES_KEY = "votes"

    def get_games_keys_set(self) -> set:
        """
        Retrieves a set of all game keys associated with the current poll. Mostly used in tests.

        Returns
        -------
        set of str
            A set containing the unique keys of all games in the poll, in the format of game identifiers,
            e.g., {'adg', 'bolt_action', 'frostgrave', 'malifaux', 'saga'}.

        """
        return set([e[KEY] for e in self.games.values()])

    def get_games_button_ids_list(self) -> list:
        """
        Retrieves a list of all button IDs associated with the current poll. Mostly used for tests.

        Returns
        -------
        list of str
            A list containing the button IDs of all games in the poll, in the format of unique
            identifiers, e.g., ['g_adg_009828688', 'g_bolt_action_871796500',
            'g_frostgrave_839799436', 'g_malifaux_594148779', 'g_saga_084217325'].
        """
        return list(self.games.keys())

    def button_id_to_element_key(self, button_id: str) -> str:
        """
        Converts a button ID to its corresponding element key.

        Parameters
        ----------
        button_id : str
            The button ID to be mapped to an element key.

        Returns
        -------
        str
            The element key associated with the given button ID.

        Raises
        ------
        ButtonIdNotPoll
            If the button ID is not found in the poll's data.
        """
        data_dict = self.others if button_id in self.others else self.games
        if button_id not in data_dict:
            raise ButtonIdNotInPoll(button_id, self.games)

        return data_dict[button_id][KEY]

    @classmethod
    async def get_bot_at_restart(cls, bot, db: DbConnector, poll_record):
        print(poll_record[cls.POLL_KEY])
        channel = await bot.fetch_channel(poll_record[cls.POLL_KEY])
        logger.debug(channel)
        return cls(db, channel, poll_record)
