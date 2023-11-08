import argparse
import json
import os
import random
import re

miniatures_games = ["Art de la guerre", "A song of ice and fire", "Bolt action", "Dragon rampant", "Frostgrave",
                    "Batailles empire", "Blitzkrieg", "Blood red skies", "Briskars", "Congo", "Core space",
                    "Dracula's america", "Lion rampant", "Malifaux", "Mousquets et Tomahawks", "Principles of war",
                    "Saga",
                    "Stargrave", "Gang of Rome", "Guildball", "Khârn Ages", "Savage core", "Star wars armada",
                    "Star wars legion",
                    "Star wars shatterpoint", "Jugula"]

board_games = ["Ave Tenebrae", "Dune", "Twilight Imperium", "La Guerre de l'Anneau", "La Quête des Terres du Milieu",
               "Firefly", "Western legends"]


def snake_string(input_string):
    input_string = input_string.lower()
    input_string = re.sub(r'[^a-z]+', '_', input_string)
    return input_string


def make_key(name, board=False):
    prefix = "GAM"
    typ = "M"
    if board:
        typ = "B"

    return prefix + typ + "_" + snake_string(name)[0:20] + "_" + format(random.randrange(0, 10 ** 9), '09d')


def make_json(name, board=False):
    typ = "Miniatures"
    if board:
        typ = "Board"

    return {
        "key": make_key(name, board),
        "long": name,
        "short": name,
        "type": typ
    }


def main():
    parser = argparse.ArgumentParser(description="Create JSON game files from games names.")
    parser.add_argument("-f", "--force", action="store_true", help="Force overwriting files.", default=False)
    args = parser.parse_args()

    for g in miniatures_games:
        filename = f"{snake_string(g)}.json"
        if args.force or not os.path.exists(filename):
            with open(f"../games/data/fr/figurines/{filename}", "w") as f:
                json.dump(make_json(g), f, indent=4)

    for g in board_games:
        filename = f"{snake_string(g)}.json"
        if args.force or not os.path.exists(filename):
            with open(f"../games/data/fr/plateau/{filename}", "w") as f:
                json.dump(make_json(g, True), f, indent=4)


if __name__ == "__main__":
    main()
