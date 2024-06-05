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


def read_and_sort_json_files(directory):
    # Initialize an empty list to store the JSON data
    items = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                item = {'long': data['long'], 'short': data['short']}
                items.append(item)

    # Sort the list of items by the "long" field
    sorted_items = sorted(items, key=lambda x: x.get('long', 0))

    return sorted_items


# Call the function and print the sorted list
sorted_figurines = read_and_sort_json_files('fr/figurines')
sorted_boards = read_and_sort_json_files('fr/plateau')

games = {"miniatures": sorted_figurines, "boards": sorted_boards}

key_value = "679058299836039192"
_filter = {'key': key_value}
update = {'$set': {'games': games}}

# Perform the update
result = db["guilds"].update_one(_filter, update)
