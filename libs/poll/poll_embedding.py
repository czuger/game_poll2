"""
This module mainly create the content of the poll. The part that show the status of the poll
(basically what games players have selected).
"""
import discord

from libs.poll.poll import Poll


def __get_user_names(users_ids, guild):
    """
    Retrieves the display names of users in a guild based on their user IDs.

    Parameters
    ----------
    users_ids : list of int
        List of user IDs.
    guild : discord.Guild
        The Discord guild object.

    Returns
    -------
    list of str
        Sorted list of user display names.
    """
    user_names = []
    for user_id in users_ids:
        user = guild.get_member(int(user_id))
        if user:
            name = user.display_name
            user_names.append(name)
        else:
            print(f"Cant find user for {user_id}")
    return ",".join(sorted(user_names))


async def get_players_embed(database, channel):
    """
    Create the status content of the poll.
      * Show the title
      * Show each activity / game followed with a list of user that had checked this activity / game

    Parameters
    ----------
    database : pymongo.database.Database
        The database object.
    channel : discord.abc.GuildChannel
        The Discord channel object.

    Returns
    -------
    discord.Embed
        The embed object displaying the poll selections.
    """
    embed = discord.Embed(title="A quoi allez vous jouer ?", color=discord.Color.blue())
    poll = await Poll.find(database, channel)

    for other in poll.others.values():
        if other["players"]:
            embed.add_field(
                name="", value=other["emoji"] + " **" + other["long"] + "** : " + __get_user_names(other["players"],
                                                                                                   channel.guild),
                inline=False)

    for game in poll.games.values():
        if game["players"]:
            embed.add_field(
                name="",
                value=" **" + game["long"] + "** : " + __get_user_names(game["players"], channel.guild),
                inline=False)

    return embed