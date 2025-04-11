import json
import logging.handlers

from poll.libs.gamebot import GameBot
from poll.libs.misc.bot.auto_refresh_poll import auto_refresh_poll
from poll.libs.misc.logging.set_logging import set_logging
from poll.libs.misc.project_root import find_project_root
from poll.orm.database import DbConnector
from poll.orm.redis import redis_connection

if __name__ == "__main__":
    set_logging()

    db = DbConnector()
    db.connect()

    redis_client = redis_connection()

    bot = GameBot(db, redis_client)


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore messages sent by the bot itself

        await auto_refresh_poll(db, message)
        await bot.process_commands(message)  # Process commands if there are any


    root_dir = find_project_root()
    with open(root_dir / "config.json", 'r') as f:
        config = json.load(f)

        print(config["discord"]["token"])
        bot.gpt_key = config["gpt"]
        bot.run(config["discord"]["token"], log_level=logging.INFO)
