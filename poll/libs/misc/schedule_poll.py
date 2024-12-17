import logging
from datetime import datetime
from datetime import timedelta

from poll.libs.dat.database import DbConnector
from poll.libs.misc.set_logging import SCHEDULE_POLL_LOG_NAME
from poll.libs.poll.poll import Poll
from poll.libs.poll.poll_embedding import get_players_embed
from poll.libs.poll.poll_view import PollView

logger = logging.getLogger(SCHEDULE_POLL_LOG_NAME)

# We will show the poll, n days ago
DAYS_AGO = 6

french_day_names = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


async def __show_poll_by_channel(channel, db: DbConnector, poll: Poll):
    pv = PollView()

    await pv.initialize_view(db, poll)
    embed = await get_players_embed(db, channel)
    await channel.send("", embed=embed, view=pv)


async def schedule_poll(db: DbConnector, ctx, day: int = None):
    """
    You call this function with a number, the number will be the number of the day in the week.
    0 Is monday
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

                poll_object = await Poll.find(db, discord_channel)
                await poll_object.reset_votes()
                await __show_poll_by_channel(discord_channel, db, poll_object)

                await db.poll_instances.update_one(
                    {'key': poll['key']},
                    {'$set': {'misc.last_schedule': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
                )
        else:
            logger.debug(f"last_schedule = {last_schedule}")
