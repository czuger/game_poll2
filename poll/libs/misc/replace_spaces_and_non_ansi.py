import re


def replace_spaces_and_non_ansi(input_string):
    """
    Replace all spaces and all non-ANSI characters in the input_string with underscores.

    Parameters:
    input_string (str): The string to be processed.

    Returns:
    str: The processed string with spaces and non-ANSI characters replaced by underscores.
    """
    input_string = input_string.lower()
    return re.sub(r'[^a-z0-9]', '_', input_string)
