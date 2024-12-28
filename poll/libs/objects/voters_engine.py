import logging

from poll.libs.misc.logging.set_logging import VOTERS_ENGINE_LOG_NAME

# Configure the logger for the voters engine
logger = logging.getLogger(VOTERS_ENGINE_LOG_NAME)


class ElementNotInVotesDict(RuntimeError):
    """
    Exception raised when an element is not found in the poll.votes dictionary.
    """

    def __init__(self, element_key: str, votes: dict):
        message = f"{element_key} not found in {votes}"
        super().__init__(message)
