import json
import logging.handlers

from poll.libs.gamebot import GameBot
from poll.libs.misc.bot.auto_refresh_poll import track_channel_activity
from poll.libs.misc.logging.set_logging import set_logging
from poll.libs.misc.project_root import find_project_root
from poll.libs.objects.database import DbConnector

if __name__ == "__main__":
    set_logging()

    db = DbConnector()
    db.connect()
    bot = GameBot(db)


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore messages sent by the bot itself

        await track_channel_activity(message)
        await bot.process_commands(message)  # Process commands if there are any


    root_dir = find_project_root()
    with open(root_dir / "config.json", 'r') as f:
        config = json.load(f)

        print(config["discord"]["token"])
        bot.run(config["discord"]["token"], log_level=logging.INFO)
