from datetime import datetime, timedelta

from poll.misc.constants import OTHER_BUTTONS
from poll.misc.params_bundle import ParamsBundle
from poll.orm.guild_orm_object import VotesData


def select_game_to_remove(params_b: ParamsBundle) -> str:
    """
    Select a game to remove based on vote count and time since last vote.

    Games with fewer votes and older last votes are prioritized for removal.

    Returns
    -------
    str or None
        The game identifier that should be removed, or None if no games exist

    Notes
    -----
    - For games without a last_vote timestamp, the oldest timestamp from other games is used
    - If no games have a timestamp, datetime.now() is used as the reference
    """

    old_in_the_past = datetime.now() - timedelta(days=60)
    game_votes_elements = {e: params_b.guild.total_votes_data.get(e, VotesData(last_vote=old_in_the_past)) for e in
                           params_b.poll.poll_elements.keys() if
                           e not in OTHER_BUTTONS}

    # Calculate scores for each game
    game_scores = []

    # Find min and max values for vote normalization
    vote_counts = [data.total_votes_count for data in game_votes_elements.values()]
    min_votes = min(vote_counts)
    max_votes = max(vote_counts)
    vote_range = max_votes - min_votes if max_votes > min_votes else 1

    for game_id, vote_data in game_votes_elements.items():
        # Normalize vote count (0 to 1 scale, where 0 is most votes and 1 is least votes)
        vote_score = 1 - ((vote_data.total_votes_count - min_votes) / vote_range)

        # Calculate time score based on age of last vote
        # Use the existing timestamp or the oldest timestamp if None
        last_vote_time = vote_data.last_vote if vote_data.last_vote is not None else old_in_the_past
        time_diff = (datetime.now() - last_vote_time).total_seconds()

        # Use a time scaling that approaches 1 for older votes
        time_score = time_diff / (time_diff + 86400)  # 86400 seconds = 1 day

        # Combine scores (equal weight to votes and time)
        combined_score = 0.5 * vote_score + 0.5 * time_score

        game_scores.append((game_id, combined_score))

    # Sort by score (highest score = most likely to be removed)
    game_scores.sort(key=lambda x: x[1], reverse=True)

    # Return the game ID with the highest score
    return game_scores[0][0]
