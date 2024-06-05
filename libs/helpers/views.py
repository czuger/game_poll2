def sort_and_split_by_chunks(input_dict: dict, chunk_size=25) -> list:
    """
    Due to some limitation of discord, we can't have views with more than 25 objects.
    """
    sorted_dict = dict(sorted(input_dict.items()))

    dict_items = list(sorted_dict.items())
    return [dict(dict_items[i:i + chunk_size]) for i in range(0, len(dict_items), chunk_size)]
