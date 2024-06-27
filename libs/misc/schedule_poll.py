import logging
from datetime import datetime
from datetime import timedelta

from libs.dat.database import DbConnector
from libs.gamebot_commands import __show_poll_by_channel
from libs.poll.poll import Poll

logger = logging.getLogger(__name__)

# We will show the poll, n days ago
DAYS_AGO = 5

french_day_names = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


async def schedule_poll(db: DbConnector, ctx, day: int = None):
    """
    You call this function with a number, the number will be the number of the day in the week.
    """
    if day is None:
        day = datetime.today().weekday()

    if 0 <= day <= 6:
        record = await db.poll_instances.find_one({Poll.POLL_KEY: str(ctx.channel.id)})
        print(ctx.channel.id, record)
        if record:
            result = await db.poll_instances.update_one(
                {'_id': record['_id']},
                {'$set': {'misc.schedule': day}}
            )
            if result.modified_count > 0 or result.upserted_id:
                day_name = french_day_names[day]
                await ctx.send(f"Le sondage est planifié le {day_name}.", delete_after=10)
            else:
                await ctx.send("Le jour du sondage était déjà fixé à cette valeur.", delete_after=10)
        else:
            await ctx.send("Aucun sondage n'existe pour ce canal.", delete_after=10)
    else:
        await ctx.send("Jour invalide. Veuillez utiliser un nombre de 0 (Lundi) à 6 (Dimanche).", delete_after=10)


async def clear_votes(db, poll):
    # We need to reset all votes
    for game in poll["buttons"]["games"].keys():
        await db.poll_instances.update_one(
            {'key': poll['key']},
            {'$set': {f'buttons.games.{game}.players': []}}
        )
    for other in poll["buttons"]["others"].keys():
        await db.poll_instances.update_one(
            {'key': poll['key']},
            {'$set': {f'buttons.others.{other}.players': []}}
        )


async def check_schedules_for_polls(db: DbConnector, bot):
    """
    This function is periodically checked. If the date of the poll is now() - DAYS_AGO, then we reset the poll voters.
    """
    days_ago = datetime.now() - timedelta(days=DAYS_AGO)

    planning_day = (datetime.now() + timedelta(days=DAYS_AGO)).weekday()
    logger.debug(f"In check_schedules_for_polls : planning_day = {planning_day}")
    polls = await db.poll_instances.find({'misc.schedule': planning_day}).to_list(None)

    for poll in polls:
        logger.debug(f"In check_schedules_for_polls : poll of the day = {poll}")
        last_schedule = poll['misc'].get('last_schedule')

        if not last_schedule or datetime.strptime(last_schedule, '%Y-%m-%d %H:%M:%S') < days_ago:
            channel_id = int(poll['key'])
            discord_channel = bot.get_channel(channel_id)
            if discord_channel:
                logger.debug("Will reset poll")

                await clear_votes(db, poll)
                db_poll = await Poll.find(db, discord_channel)
                await __show_poll_by_channel(discord_channel, db, db_poll)

                await db.poll_instances.update_one(
                    {'key': poll['key']},
                    {'$set': {'misc.last_schedule': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
                )
        else:
            logger.debug(f"last_schedule = {last_schedule}")