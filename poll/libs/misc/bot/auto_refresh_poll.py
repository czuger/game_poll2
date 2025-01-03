# Create a dictionary to store the count of lines per channel
import logging

from poll.libs.misc.logging.set_logging import AUTO_REFRESH_LOG_NAME
from poll.libs.objects.poll import Poll
from poll.libs.objects.poll import PollNotFound
from poll.libs.poll.poll_embedding import get_players_embed
from poll.libs.poll.poll_view import PollView

logger = logging.getLogger(AUTO_REFRESH_LOG_NAME)

channel_message_count = {}

# Define a constant for the maximum message count before reset
MAX_MESSAGE_COUNT = 15


# Function to update message count and repost poll if it exceeds MAX_MESSAGE_COUNT
async def auto_refresh_poll(db, message):
    """
    Update the message count for the given channel and repost the poll if it exceeds MAX_MESSAGE_COUNT.

    Parameters:
    message (discord.Message): The message object containing the channel and content information.
    """
    channel_id = message.channel.id
    lines = message.content.count('\n') + 1  # Count the number of lines in the message

    # Update the message count for the channel
    if channel_id in channel_message_count:
        channel_message_count[channel_id] += lines
    else:
        channel_message_count[channel_id] = lines

    # Optionally, print the message count for each channel (for debugging purposes)
    logger.debug(f'Line count for channel {channel_id}({message.channel.name}): {channel_message_count[channel_id]}')

    # Check if the count exceeds the max value
    if channel_message_count[channel_id] > MAX_MESSAGE_COUNT:
        logger.debug(f'Channel {channel_id} exceeded {MAX_MESSAGE_COUNT} lines. Resetting count and reposting poll.')

        try:
            poll = await Poll.find(db, message.channel, create_if_not_exist=False)
            logger.debug(f'Poll= {poll}')

            pv = PollView()
            logger.debug(f'PollView= {pv}')

            await pv.initialize_view(db, poll)
            embed = await get_players_embed(db, message.channel)
            logger.debug(f'embed= {embed}')

            result = await message.channel.send("", embed=embed, view=pv)
            logger.debug(f'send_result= {result}')

            channel_message_count[channel_id] = 0  # Reset the count
        except PollNotFound:
            logger.debug(
                f'Channel {channel_id} poll does not exist. Reset aborted.')
            channel_message_count[channel_id] = -100
