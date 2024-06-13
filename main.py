import json
import logging.handlers

from libs.dat.database import DbConnector
from libs.gamebot import GameBot
from libs.gamebot_commands import command_poll
from libs.gamebot_commands import reset_command
from libs.misc.project_root import find_project_root
from libs.misc.set_logging import set_logging

set_logging()

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
