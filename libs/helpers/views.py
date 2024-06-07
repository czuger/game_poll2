def sort_and_split_by_chunks(l: list, chunk_size=25) -> list:
    """
    Due to some limitation of discord, we can't have views with more than 25 objects.
    """
    return [l[i:i + chunk_size] for i in range(0, len(l), chunk_size)]
