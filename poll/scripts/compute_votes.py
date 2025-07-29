import logging
from datetime import datetime
from datetime import timedelta
from typing import Dict

from pymongo import MongoClient

from poll.libs.misc.config import ConfigReader
from poll.libs.misc.logging.set_logging import COMPUTE_VOTES_LOG_NAME
from poll.libs.misc.logging.set_logging import set_logging

logger = logging.getLogger(COMPUTE_VOTES_LOG_NAME)


def compute_game_score(total_votes: int, last_votes: int) -> float:
    """
    Compute game score where:
    - last_votes = integer part
    - total_votes = decimal part (as percentage of 100)
    """
    # Ensure total_votes doesn't exceed 9999 to avoid overflow
    decimal_part = min(abs(total_votes), 9999) / 10000.0

    # Combine: last_votes as integer + total_votes as decimal
    score = last_votes + decimal_part

    return score


class VoteCalculator:
    def __init__(self, config_reader: ConfigReader):
        connection_string = config_reader.get_mongo_connection_string()
        self.client = MongoClient(connection_string)
        self.db = self.client[config_reader.get_db_name()]
        self.votes = self.db.votes
        self.guilds = self.db.guilds

    def get_vote_totals(self) -> Dict[str, int]:
        """Get grand total votes for all games"""
        pipeline = [
            {
                "$unwind": "$votes"  # Unwind the votes array
            },
            {
                "$group": {
                    "_id": "$votes.gk",  # Group by game key from the votes subdocument
                    "total": {"$sum": "$votes.vc"}  # Sum the vote counts
                }
            }
        ]

        result = self.votes.aggregate(pipeline)
        return {doc["_id"]: doc["total"] for doc in result}

    def get_last_months_totals(self) -> Dict[str, int]:
        """Get vote totals for last 2 months"""
        months_ago = datetime.now() - timedelta(days=30 * 2)

        pipeline = [
            {
                "$unwind": "$votes"  # Unwind the votes array
            },
            {
                "$match": {
                    "votes.t": {"$gte": months_ago.isoformat()}  # Filter by timestamp in votes subdocument
                }
            },
            {
                "$group": {
                    "_id": "$votes.gk",  # Group by game key from votes subdocument
                    "total": {"$sum": "$votes.vc"}  # Sum vote counts from votes subdocument
                }
            }
        ]

        result = self.votes.aggregate(pipeline)
        return {doc["_id"]: doc["total"] for doc in result}

    def update_game_votes(self, game_key: str, total_votes: int, last_votes: int):
        """Update a single game's vote totals"""
        try:
            result = self.guilds.update_one(
                {f"games.{game_key}": {"$exists": True}},
                {
                    "$set": {
                        f"games.{game_key}.total_votes": total_votes,
                        f"games.{game_key}.last_votes": last_votes,
                        f"games.{game_key}.votes_score": compute_game_score(total_votes, last_votes)
                    }
                }
            )

            if result.matched_count > 0:
                logger.info(f"✓ Updated {game_key}: total_votes={total_votes}, last_votes={last_votes}")
            else:
                logger.info(f"⚠ Game '{game_key}' not found in games collection")

        except Exception as e:
            logger.info(f"✗ Error updating {game_key}: {e}")

    def update_all_games(self):
        """Main method to update all games with vote totals"""
        logger.info("Calculating vote totals...")

        # Get vote totals
        grand_totals = self.get_vote_totals()
        logger.info(f"grand_totals = {grand_totals}")
        last_2_months_totals = self.get_last_months_totals()
        logger.info(f"last_2_months_totals = {last_2_months_totals}")

        # Get all unique game keys
        all_game_keys = set(grand_totals.keys()) | set(last_2_months_totals.keys())

        logger.info(f"\nUpdating {len(all_game_keys)} games...")

        # Update each game
        for game_key in all_game_keys:
            logger.info(f"Processing key = {game_key}")
            total_votes = grand_totals.get(game_key, 0)
            last_votes = last_2_months_totals.get(game_key, 0)

            logger.info(f"total_votes, last_votes = {total_votes}, {last_votes}")

            self.update_game_votes(game_key, total_votes, last_votes)

        logger.info(f"\n✓ Finished updating all games")

    def close(self):
        """Close database connection"""
        self.client.close()


def main():
    # Import and initialize your ConfigReader

    config_reader = ConfigReader(config_file_path="config.json")  # Initialize with any required parameters

    set_logging(config_reader)

    # Initialize calculator
    calculator = VoteCalculator(config_reader)

    try:
        # Update all games
        logger.info("About to update all games.")
        calculator.update_all_games()

        # logger.info(len(game_keys))

        # calculator.find_lowest_voted_game(list(game_keys))
        # pass

    except Exception as e:
        logger.info(f"Error: {e}")

    finally:
        # Clean up
        calculator.close()


if __name__ == "__main__":
    main()
