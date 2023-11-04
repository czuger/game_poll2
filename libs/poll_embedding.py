import discord

from libs.poll import Poll


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


def add_selection(guild, poll, selection, users, games, others):
    users_list = __get_user_names(users, guild)
    if len(users_list) > 0:
        users_line = ",".join(users_list)

        if selection in poll.games:
            selection_object = poll.games[selection]
            games.append((selection_object["long"], users_line))
        elif selection in poll.others:
            selection_object = poll.others[selection]
            others.append((selection_object["long"], users_line))
        else:
            raise RuntimeError(f"Unable to find {selection}")

    return games, others


async def get_players_embed(database, channel):
    embed = discord.Embed(title="A quoi allez vous jouer ?", color=discord.Color.blue())
    poll = await Poll.find(database, str(channel.id))

    poll_db_obj = poll.get_poll_db_object()

    if Poll.SELECTIONS_KEY in poll_db_obj:
        selections = poll_db_obj[Poll.SELECTIONS_KEY]
        games = []
        others = []

        for selection, users in selections.items():
            (games, others) = add_selection(channel.guild, poll, selection, users, games, others)

        games.sort(key=lambda x: (x[0], x[1]))
        others.sort(key=lambda x: (x[0], x[1]))

        for label, users_line in others:
            embed.add_field(name="", value="**" + label + "** : " + users_line, inline=False)

        for label, users_line in games:
            embed.add_field(name="", value="**" + label + "** : " + users_line, inline=False)

    return embed
