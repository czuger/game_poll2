def sort_and_split(keys: list, chunk_size=25) -> list:
    """
    Sort a list of keys and split it into smaller chunks.

    This function addresses Discord's limitation that prevents views from containing
    more than 25 interactive elements. It sorts the input list alphabetically and
    then divides it into smaller sublists.

    Parameters
    ----------
    keys : list
        The list of items to sort and split.
    chunk_size : int, optional
        Maximum number of items per chunk, by default 25,
        which complies with Discord's UI component limits.

    Returns
    -------
    list
        A list of sublists, each containing at most `chunk_size` elements from
        the original list in sorted order.

    Examples
    --------
    >>> sort_and_split(['c', 'a', 'b'], chunk_size=2)
    [['a', 'b'], ['c']]
    """
    keys.sort()
    return [keys[i:i + chunk_size] for i in range(0, len(keys), chunk_size)]
