import json
import logging.handlers

from libs.dat.database import DbConnector
from libs.gamebot import GameBot
from libs.gamebot_commands import command_poll
from libs.misc.auto_refresh_poll import auto_refresh_poll
from libs.misc.project_root import find_project_root
from libs.misc.schedule_poll import schedule_poll
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
    async def schedule(ctx, day: int = None):
        await schedule_poll(db, ctx, day)


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore messages sent by the bot itself

        await auto_refresh_poll(db, message)
        await bot.process_commands(message)  # Process commands if there are any


    # @bot.command()
    # async def reset(ctx):
    #     await reset_command(ctx, db)

    root_dir = find_project_root()
    with open(root_dir / "config.json", 'r') as f:
        config = json.load(f)

        bot.run(config["discord"]["token"], log_level=logging.INFO)
