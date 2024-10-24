# Create a dictionary to store the count of lines per channel
import logging

from libs.misc.set_logging import AUTO_REFRESH_LOG_NAME
from libs.poll.poll import Poll
from libs.poll.poll_embedding import get_players_embed
from libs.poll.poll_view import PollView

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

    # Check if the count exceeds the max value
    if channel_message_count[channel_id] > MAX_MESSAGE_COUNT:
        logger.debug(f'Channel {channel_id} exceeded {MAX_MESSAGE_COUNT} lines. Resetting count and reposting poll.')

        poll = await Poll.find(db, message.channel, create_if_not_exist=False)
        logger.debug(f'Poll {poll}')

        if poll:
            pv = PollView()

            await pv.initialize_view(db, poll)
            embed = await get_players_embed(db, message.channel)
            await message.channel.send("", embed=embed, view=pv)

            channel_message_count[channel_id] = 0  # Reset the count
        else:
            logger.debug(
                f'Channel {channel_id} poll does not exist. Reset aborted.')

    # Optionally, print the message count for each channel (for debugging purposes)
    logger.debug(f'Line count for channel {channel_id}: {channel_message_count[channel_id]}')
