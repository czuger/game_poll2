import re
import random
import json
import os

miniatures_games = ["Batailles empire", "Blitzkrieg", "Blood red skies", "Briskars", "Congo", "Core space",
                    "Dracula's america",
                    "Stargrave", "Gang of Rome", "Guildball", "Khârn Ages", "Savage core", "Star wars armada",
                    "Star wars legion",
                    "Star wars shatterpoint", "Jugula"]

board_games = ["Ave Tenebrae", "Dune", "Twilight Imperium", "La Guerre de l'Anneau", "La Quête des Terres du Milieu"]


def snake_string(input_string):
    input_string = input_string.lower()
    input_string = re.sub(r'[^a-z]+', '_', input_string)
    return input_string


def make_key(name, board=False):
    prefix = "GAM"
    typ = "M"
    if board:
        typ = "B"

    return prefix + typ + "_" + snake_string(name)[0:20] + "_" + str(random.randrange(0, 10 ** 9))


def make_json(name, board=False):
    typ = "Miniatures"
    if board:
        typ = "Board"

    return {
        "key": make_key(name),
        "long": name,
        "short": name,
        "type": typ
    }


for g in miniatures_games:
    filename = f"{snake_string(g)}.json"
    if not os.path.exists(filename):
        with open(f"../games/data/fr/figurines/{filename}", "w") as f:
            json.dump(make_json(g), f, indent=4)

