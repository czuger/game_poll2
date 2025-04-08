from datetime import datetime

from poll.orm.guild_orm_object import GuildOrmObject


def select_game_to_remove(guild_data: GuildOrmObject) -> str:
    """
    Select a game to remove based on vote count and time since last vote.

    Games with fewer votes and older last votes are prioritized for removal.

    Parameters
    ----------
    guild_data : GuildOrmObject
        Guild data object containing total_votes_data dictionary where:
        - keys are game identifiers (str)
        - values are VotesData objects with:
          * total_votes_count : int, number of votes the game has received
          * last_vote : datetime, timestamp of the last vote (can be None)

    Returns
    -------
    str or None
        The game identifier that should be removed, or None if no games exist

    Notes
    -----
    - For games without a last_vote timestamp, the oldest timestamp from other games is used
    - If no games have a timestamp, datetime.now() is used as the reference
    """
    if not guild_data.total_votes_data:
        raise RuntimeError("guild_data.total_votes_data -> This can't be")

    # Get all games with vote data
    games_vote_data = guild_data.total_votes_data

    # Find the oldest last_vote time from all games
    oldest_time = None
    for data in games_vote_data.values():
        if data.last_vote is not None:
            if oldest_time is None or data.last_vote < oldest_time:
                oldest_time = data.last_vote

    # If no valid timestamps found, use current time
    if oldest_time is None:
        oldest_time = datetime.now()

    # Calculate scores for each game
    game_scores = []

    # Find min and max values for vote normalization
    vote_counts = [data.total_votes_count for data in games_vote_data.values()]
    min_votes = min(vote_counts)
    max_votes = max(vote_counts)
    vote_range = max_votes - min_votes if max_votes > min_votes else 1

    for game_id, vote_data in games_vote_data.items():
        # Normalize vote count (0 to 1 scale, where 0 is most votes and 1 is least votes)
        vote_score = 1 - ((vote_data.total_votes_count - min_votes) / vote_range)

        # Calculate time score based on age of last vote
        # Use the existing timestamp or the oldest timestamp if None
        last_vote_time = vote_data.last_vote if vote_data.last_vote is not None else oldest_time
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
