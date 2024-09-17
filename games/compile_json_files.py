import json
import os

from libs.misc.replace_spaces_and_non_ansi import replace_spaces_and_non_ansi


def process_json_files(directory):
    # Initialize the result dictionary with keys for miniatures and boards

    games = {}
    miniatures = []
    boards = []
    poll_defaults = []

    # Walk through all directories and subdirectories
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):  # Check if the file is a JSON file

                filepath = os.path.join(root, filename)

                # Read the JSON file
                with open(filepath, 'r') as file:
                    try:
                        data = json.load(file)

                        # Check if data is a dictionary
                        if isinstance(data, dict):
                            key_param = replace_spaces_and_non_ansi(data.get("short"))
                            data["key"] = key_param

                            if key_param is not None:
                                games[key_param] = data

                                if data.get("default"):
                                    poll_defaults.append(key_param)

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from file {filename}: {e}")
                    except Exception as e:
                        print(f"An error occurred while processing file {filename}: {e}")

    # # Define a sorting function for dictionaries by the 'short' key
    # def sort_dict_by_short(d):
    #     return dict(sorted(d.items(), key=lambda item: item[1].get("short", "")))
    #
    # # Sort the dictionaries by their 'short' entries
    # result["miniatures"] = sort_dict_by_short(result["miniatures"])
    # result["boards"] = sort_dict_by_short(result["boards"])
    # result["poll_default"] = sort_dict_by_short(result["poll_default"])

    sorted_poll_default = sorted(poll_defaults, key=lambda k: games[k]['short'])

    return {"games": games, "poll_default": sorted_poll_default}


# Usage
directory_path = 'data'
result_dict = process_json_files(directory_path)
# pprint(result_dict)

# Print or use the result dictionary
with open("games.json", "w") as f:
    json.dump(result_dict, f, indent=4)
