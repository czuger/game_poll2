import logging.handlers
from logging.handlers import RotatingFileHandler

MAX_LOG_FILE_SIZE = 20 * 1024 * 1024
BACKUP_COUNT = 5


def set_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    rotating_handler = RotatingFileHandler("/var/log/gamebot/gamebot.log", maxBytes=MAX_LOG_FILE_SIZE,
                                           backupCount=BACKUP_COUNT, encoding='utf-8')
    logger.addHandler(rotating_handler)

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    rotating_handler = RotatingFileHandler("/var/log/gamebot/discord.log", maxBytes=MAX_LOG_FILE_SIZE,
                                           backupCount=BACKUP_COUNT, encoding='utf-8')
    logger.addHandler(rotating_handler)

    logger = logging.getLogger('discord.http')
    logger.setLevel(logging.DEBUG)
    rotating_handler = RotatingFileHandler("/var/log/gamebot/discord.http.log", maxBytes=MAX_LOG_FILE_SIZE,
                                           backupCount=BACKUP_COUNT, encoding='utf-8')
    logger.addHandler(rotating_handler)
