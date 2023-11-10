import discord

from libs.games import Games
from libs.poll.poll import Poll


def __get_user_names(users_ids, guild):
    user_names = []
    for user_id in users_ids:
        user = guild.get_member(int(user_id))
        if user:
            name = user.display_name
            user_names.append(name)
        else:
            print(f"Cant find user for {user_id}")
    return sorted(user_names)


def get_selection_long_name(db_games_obj: Games, game_key):
    if game_key in Poll.OTHER_BUTTONS:
        game_name = Poll.OTHER_BUTTONS[game_key]["long"]
    elif game_key in db_games_obj.dict:
        game_name = db_games_obj.dict[game_key]["long"]
    else:
        raise RuntimeError(f"game {game_key} does not exist in Games collection")

    return game_name


def add_selection(db_games_obj: Games, guild, poll, game_key, users, games, others):
    users_list = __get_user_names(users, guild)
    if len(users_list) > 0:
        users_line = ",".join(users_list)

        if game_key in poll.OTHER_BUTTONS:
            game_name = get_selection_long_name(db_games_obj, game_key)
            others.append((game_name, users_line))
        elif game_key in poll.selections:
            game_name = get_selection_long_name(db_games_obj, game_key)
            games.append((game_name, users_line))
        else:
            raise RuntimeError(f"Unable to find {game_key}")

    return games, others


async def get_players_embed(database, channel):
    embed = discord.Embed(title="A quoi allez vous jouer ?", color=discord.Color.blue())
    poll = await Poll.find(database, str(channel.id))

    db_games_obj = await Games.get_games(database)

    games = []
    others = []

    for selection, users in poll.selections.items():
        (games, others) = add_selection(db_games_obj, channel.guild, poll, selection, users, games, others)

    games.sort(key=lambda x: (x[0], x[1]))
    others.sort(key=lambda x: (x[0], x[1]))

    for label, users_line in others:
        embed.add_field(name="", value="**" + label + "** : " + users_line, inline=False)

    for label, users_line in games:
        embed.add_field(name="", value="**" + label + "** : " + users_line, inline=False)

    return embed
