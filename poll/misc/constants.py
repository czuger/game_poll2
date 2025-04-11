import discord

KEY = "key"
LONG_NAME = "long"

DEFAULT_DELETE_AFTER = 120

OTHER_BUTTONS = {
    "present_with_key": {"key": "present_with_key", "short": "Clés", "long": "Présent avec les clés", "emoji": "🔑",
                         "style": discord.ButtonStyle.green},
    # "tournament_orga": {"key": "tournament_orga", "short": "Tournoi/Orga",
    #                     "long": "En tournoi ou en orga de tournoi", "emoji": "🍺",
    #                     "style": discord.ButtonStyle.success},
    "other": {"key": "other", "short": "Autre", "long": "Autre activité", "emoji": "♟️",
              "style": discord.ButtonStyle.blurple},
    "away": {"key": "away", "short": "Absent", "long": "Absent", "emoji": "⛱️",
             "style": discord.ButtonStyle.blurple},
    "add": {"key": "add", "short": "Ajouter", "long": "Ajouter un jeu", "emoji": "🧩",
            "style": discord.ButtonStyle.grey, "action": "add_game"},
}

MAX_ROWS_IN_POLL = 4
MAX_COLS_IN_POLL = 5
