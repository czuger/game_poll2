import json
import os

from poll.libs.objects.database import DbConnector


class BotTest:

    def __init__(self):
        self.db = None

    def set_up(self):
        self.db = DbConnector()
        self.db.connect("games_database_tests")
        self.db.clear_db()

        if os.path.exists("fixtures"):
            fixtures_path = "fixtures"
        else:
            fixtures_path = "tests/fixtures"

        for root, dirs, files in os.walk(fixtures_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as json_file:
                        try:
                            json_data = json.load(json_file)
                            self.db.games.insert_one(json_data)
                        except Exception as e:
                            print(f"Error inserting data from {file_path}: {str(e)}")
