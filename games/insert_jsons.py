import json
import os

from pymongo import MongoClient

from libs.misc.project_root import find_project_root

root_dir = find_project_root()
with open(root_dir / "config.json", 'r') as f:
    config = json.load(f)
    mongo = config["mongo"]

client = MongoClient(mongo["server"], 27017, username=mongo["user"], password=mongo["pass"])
db = client["games_database"]
games_collection = db["games"]


def insert_or_update_json_data(data):
    # Use the "short" field as a query to find existing records
    query = {"key": data["key"]}
    existing_record = games_collection.find_one(query)

    if existing_record:
        # Update the existing record with the new data
        games_collection.replace_one(query, data)
        print(f"Updated data with short value '{data['key']}' in MongoDB.")
    else:
        # Insert a new record if the "short" value doesn't exist in the collection
        games_collection.insert_one(data)
        print(f"Inserted data with short value '{data['key']}' into MongoDB.")


base_directory = "."

# Walk through subdirectories and read JSON files
for root, dirs, files in os.walk(base_directory):
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as json_file:
                try:
                    json_data = json.load(json_file)
                    insert_or_update_json_data(json_data)
                    print(f"Inserted data from {file_path} into MongoDB.")
                except Exception as e:
                    print(f"Error inserting data from {file_path}: {str(e)}")

# Close the MongoDB connection
client.close()
