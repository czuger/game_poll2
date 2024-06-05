import json
import logging
from logging.handlers import RotatingFileHandler

from libs.dat.database import DbConnector
from libs.gamebot import GameBot
from libs.gamebot_commands import command_poll
from libs.gamebot_commands import reset_command
from libs.misc.project_root import find_project_root

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
rotating_handler = RotatingFileHandler("/var/log/gamebot/gamebot.log", maxBytes=20 * 1024 * 1024, backupCount=2)
logger.addHandler(rotating_handler)

# @bot.event
# async def on_message(message):
#     print(message.channel.id, message.content)


if __name__ == "__main__":
    db = DbConnector()
    db.connect()
    bot = GameBot(db)


    @bot.command()
    async def poll(ctx):
        await command_poll(ctx, db)


    @bot.command()
    async def reset(ctx):
        await reset_command(ctx, db)


    root_dir = find_project_root()
    with open(root_dir / "config.json", 'r') as f:
        config = json.load(f)

        bot.run(config["discord"]["token"], log_level=logging.INFO)
