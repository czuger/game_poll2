import json
import logging.handlers

from poll.gamebot import GameBot
from poll.misc import auto_refresh_poll
from poll.misc import find_project_root
from poll.misc import set_logging
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
