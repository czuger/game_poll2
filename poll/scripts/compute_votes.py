from datetime import datetime, timedelta
from typing import Dict

from pymongo import MongoClient

from poll.libs.misc.config import ConfigReader

DATABASE_NAME = "games_database"  # Update with your database name


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
    def __init__(self, config_reader):
        connection_string = config_reader.get_mongo_connection_string()
        self.client = MongoClient(connection_string)
        self.db = self.client[DATABASE_NAME]
        self.votes = self.db.votes  # Adjust collection name as needed
        self.guilds = self.db.guilds  # Adjust collection name as needed

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
                print(f"✓ Updated {game_key}: total_votes={total_votes}, last_votes={last_votes}")
            else:
                print(f"⚠ Game '{game_key}' not found in games collection")

        except Exception as e:
            print(f"✗ Error updating {game_key}: {e}")

    def update_all_games(self):
        """Main method to update all games with vote totals"""
        print("Calculating vote totals...")

        # Get vote totals
        grand_totals = self.get_vote_totals()
        last_2_months_totals = self.get_last_months_totals()

        print(f"Found votes for {len(grand_totals)} games")
        print(f"Grand totals: {grand_totals}")
        print(f"Last 2 months: {last_2_months_totals}")

        # Get all unique game keys
        all_game_keys = set(grand_totals.keys()) | set(last_2_months_totals.keys())

        print(f"\nUpdating {len(all_game_keys)} games...")

        # Update each game
        for game_key in all_game_keys:
            total_votes = grand_totals.get(game_key, 0)
            last_votes = last_2_months_totals.get(game_key, 0)

            self.update_game_votes(game_key, total_votes, last_votes)

        print(f"\n✓ Finished updating all games")

    def close(self):
        """Close database connection"""
        self.client.close()

    def get_games_by_score_simple(self, guild_id: str = "487195321852624917") -> Dict:
        """
        Simple approach: get guild data and sort in Python
        """
        guild_data = self.guilds.find_one({"key": guild_id})

        if not guild_data or "games" not in guild_data:
            print(f"⚠ No games found for guild {guild_id}")
            return {}

        games_dict = {}
        for game_key, game_data in guild_data["games"].items():
            games_dict[game_key] = game_data.get("votes_score", 0)

        return games_dict

    def find_lowest_voted_game(self, game_list):
        scores_dict = self.get_games_by_score_simple()
        lowest_score = 999999999
        lowest_key = None

        games = []

        for game_key in game_list:
            games.append((scores_dict[game_key], game_key))
            if scores_dict[game_key] < lowest_score:
                lowest_score = scores_dict[game_key]
                lowest_key = game_key

        print(lowest_score, lowest_key)

        games.sort(reverse=True)
        for game in games:
            print(game)


def main():
    # Import and initialize your ConfigReader

    config_reader = ConfigReader(config_file_path="config_staging.json")  # Initialize with any required parameters

    # Initialize calculator
    calculator = VoteCalculator(config_reader)

    try:
        # Update all games
        calculator.update_all_games()

        game_keys = [
            'adg',
            'bolt_action',
            'frostgrave',
            'malifaux',
            'saga',
            'asoif',
            'v_for_victory',
            'valour___fortitude',
            'principles_of_war',
            'kings_of_war',
            'sw_legion',
            'adeptus_titanicus',
            'mousquets_et_tomahawks',
            'firefly',
            'lion_rampant',
            'blood_bowl',
            'au_contact',
            'epic',
            'dracula_s_america',
            'rumbleslam'
        ]

        print(len(game_keys))

        calculator.find_lowest_voted_game(list(game_keys))
        pass

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up
        calculator.close()


if __name__ == "__main__":
    main()
