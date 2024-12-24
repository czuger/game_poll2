import json
import logging.handlers

from poll.libs.objects.database import DbConnector
from poll.libs.gamebot import GameBot
from poll.libs.misc.bot.auto_refresh_poll import auto_refresh_poll
from poll.libs.misc.bot.gpt_test import call_chatgpt_async
from poll.libs.misc.project_root import find_project_root
from poll.libs.misc.logging.set_logging import set_logging

if __name__ == "__main__":
    set_logging()

    db = DbConnector()
    db.connect()
    bot = GameBot(db)


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore messages sent by the bot itself

        await auto_refresh_poll(db, message)
        await call_chatgpt_async(db, message, bot.gpt_key)
        await bot.process_commands(message)  # Process commands if there are any


    root_dir = find_project_root()
    with open(root_dir / "config.json", 'r') as f:
        config = json.load(f)

        print(config["discord"]["token"])
        bot.gpt_key = config["gpt"]
        bot.run(config["discord"]["token"], log_level=logging.INFO)
