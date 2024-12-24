from poll.libs.objects.guild import Guild


def sort_and_split_by_chunks(items: list, guild: Guild, chunk_size=25) -> list:
    """
    Due to some limitation of discord, we can't have views with more than 25 objects.
    """
    items.sort(key=lambda x: guild.games[x].get('short', ''))
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
