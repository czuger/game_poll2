import logging
from logging.handlers import RotatingFileHandler

# Constants for log file sizes and backups (you should replace these with actual values)
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # Example: 10 MB
BACKUP_COUNT = 5  # Number of backup files to keep

COMMANDS_NAME = "commands"
ADMINS_LOG_NAME = "admins"
POLLS_LOG_NAME = "polls"
ADD_GAMES_LOG_NAME = "add_games"
AUTO_REFRESH_LOG_NAME = "auto_refresh_poll"
SCHEDULE_POLL_LOG_NAME = "schedule_poll"
GPT_LOG_NAME = "gpt_log"
VOTERS_ENGINE_LOG_NAME = "voters_engine_log"

# Define a utility function to set up a rotating file handler with a formatter
def setup_rotating_logger(logger_name, log_file_path, log_level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Create a rotating file handler
    rotating_handler = RotatingFileHandler(log_file_path, maxBytes=MAX_LOG_FILE_SIZE, backupCount=BACKUP_COUNT,
                                           encoding='utf-8')

    # Set the logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    rotating_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(rotating_handler)

    # Now no logs will be sent to stderr, only to the file
    logger.propagate = False

    return logger


def set_logging():
    setup_rotating_logger(__name__, "/var/log/gamebot/gamebot.log")
    setup_rotating_logger('discord', "/var/log/gamebot/discord.log")
    setup_rotating_logger('discord.http', "/var/log/gamebot/discord.http.log")
    setup_rotating_logger(COMMANDS_NAME, f"/var/log/gamebot/{COMMANDS_NAME}.log")
    setup_rotating_logger(ADMINS_LOG_NAME, f"/var/log/gamebot/{ADMINS_LOG_NAME}.log")
    setup_rotating_logger(POLLS_LOG_NAME, f"/var/log/gamebot/{POLLS_LOG_NAME}.log", logging.DEBUG)
    setup_rotating_logger(ADD_GAMES_LOG_NAME, f"/var/log/gamebot/{ADD_GAMES_LOG_NAME}.log", logging.DEBUG)
    setup_rotating_logger(AUTO_REFRESH_LOG_NAME, f"/var/log/gamebot/{AUTO_REFRESH_LOG_NAME}.log", logging.DEBUG)
    setup_rotating_logger(SCHEDULE_POLL_LOG_NAME, f"/var/log/gamebot/{SCHEDULE_POLL_LOG_NAME}.log", logging.DEBUG)
    setup_rotating_logger(GPT_LOG_NAME, f"/var/log/gamebot/{GPT_LOG_NAME}.log", logging.DEBUG)
    setup_rotating_logger(VOTERS_ENGINE_LOG_NAME, f"/var/log/gamebot/{VOTERS_ENGINE_LOG_NAME}.log", logging.DEBUG)