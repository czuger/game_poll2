import json
import os
import re


def replace_spaces_and_non_ansi(input_string):
    """
    Replace all spaces and all non-ANSI characters in the input_string with underscores.

    Parameters:
    input_string (str): The string to be processed.

    Returns:
    str: The processed string with spaces and non-ANSI characters replaced by underscores.
    """
    input_string = input_string.lower()
    return re.sub(r'[^a-z0-9]', '_', input_string)


def process_json_files(directory):
    # Initialize the result dictionary with keys for miniatures and boards
    result = {"miniatures": {}, "boards": {}, "poll_default": {}}

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
                            item_type = data.get("type")
                            key_param = replace_spaces_and_non_ansi(data.get("short"))
                            data["key"] = key_param

                            if key_param is not None:
                                if item_type == "Miniatures":
                                    result["miniatures"][key_param] = data
                                elif item_type == "Board":
                                    result["boards"][key_param] = data

                                if data.get("default"):
                                    result["poll_default"][key_param] = data

                            if "default" in data:
                                del data["default"]

                            del data["type"]

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from file {filename}: {e}")
                    except Exception as e:
                        print(f"An error occurred while processing file {filename}: {e}")

    # Define a sorting function for dictionaries by the 'short' key
    def sort_dict_by_short(d):
        return dict(sorted(d.items(), key=lambda item: item[1].get("short", "")))

    # Sort the dictionaries by their 'short' entries
    result["miniatures"] = sort_dict_by_short(result["miniatures"])
    result["boards"] = sort_dict_by_short(result["boards"])
    result["poll_default"] = sort_dict_by_short(result["poll_default"])

    return result


# Usage
directory_path = 'data'
result_dict = process_json_files(directory_path)
# pprint(result_dict)

# Print or use the result dictionary
with open("games.json", "w") as f:
    json.dump(result_dict, f, indent=4)
