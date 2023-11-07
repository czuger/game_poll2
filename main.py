import logging

from libs.database import DbConnector

from libs.gamebot import GameBot
from libs.gamebot_commands import command_poll
from libs.gamebot_commands import reset_command

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


    with open("discord_token.txt", 'r') as f:
        bot.run(f.read(), log_level=logging.INFO)
