# Create a dictionary to store the count of lines per channel
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from poll.libs.misc.logging.set_logging import AUTO_REFRESH_LOG_NAME
from poll.libs.objects.poll import Poll
from poll.libs.objects.poll import PollNotFound
from poll.libs.poll.poll_embedding import get_players_embed
from poll.libs.poll.poll_view import PollView

logger = logging.getLogger(AUTO_REFRESH_LOG_NAME)


@dataclass
class ChannelInfo:
    lines_count: int
    last_message: datetime


channel_message_count = {}

MAX_MESSAGE_COUNT = 15


async def track_channel_activity(message):
    """Called each time a user type a message in a channel."""
    channel_id = message.channel.id
    lines = message.content.count('\n') + 1
    current_time = datetime.now()

    if channel_id in channel_message_count:
        channel_info = channel_message_count[channel_id]
        channel_info.lines_count += lines
        channel_info.last_message = current_time
    else:
        channel_message_count[channel_id] = ChannelInfo(lines_count=lines, last_message=current_time)

    logger.debug(
        f'Line count for channel {channel_id}({message.channel.name}): {channel_message_count[channel_id].lines_count}')


async def check_channel_refresh(db, bot):
    """Called each 30 minutes. Add a new poll if people stopped talking."""
    now = datetime.now()
    ten_minutes = timedelta(minutes=30)

    for channel_id in channel_message_count.keys():
        channel_info = channel_message_count[channel_id]

        if (channel_info.lines_count > MAX_MESSAGE_COUNT and
                channel_info.last_message < now - ten_minutes):
            logger.debug(
                f'Channel {channel_id} exceeded {MAX_MESSAGE_COUNT} lines and has been inactive for 10+ minutes. '
                f'Resetting count and reposting poll.')

            try:
                channel = bot.get_channel(int(channel_id))
                if not channel:
                    logger.error(f'Could not find channel with ID {channel_id}')
                    continue

                poll = await Poll.find(db, channel, create_if_not_exist=False)
                logger.debug(f'Poll= {poll}')

                pv = PollView()
                logger.debug(f'PollView= {pv}')

                await pv.initialize_view(db, poll)
                embed = await get_players_embed(db, channel)
                logger.debug(f'embed= {embed}')

                result = await channel.send("", embed=embed, view=pv)
                logger.debug(f'send_result= {result}')

                channel_info.lines_count = 0
            except PollNotFound:
                logger.debug(f'Channel {channel_id} poll does not exist. Reset aborted.')
                channel_info.lines_count = -100
