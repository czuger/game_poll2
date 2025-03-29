from poll.libs.gamebot import GameBot
from poll.libs.misc.bot.auto_refresh_poll import track_channel_activity
from poll.libs.misc.config import ConfigReader
from poll.libs.misc.logging.set_logging import set_logging
from poll.libs.objects.database import DbConnector

if __name__ == "__main__":

    config = ConfigReader("config.json")

    set_logging(config)

    db = DbConnector()
    db.connect(config)
    bot = GameBot(db)


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore messages sent by the bot itself

        await track_channel_activity(message)
        await bot.process_commands(message)  # Process commands if there are any


    bot.run(config.get_discord_token(), log_level=config.get_logging_level())
