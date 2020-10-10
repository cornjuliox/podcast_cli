from typing import List


def exclude_keys(d: dict, keys: List[str]):
    """
    Returns a dictionary containing all keys
    except the ones specified in "keys".

    input:
    d - dictionary, any Python dictionary with key+value pairs
    keys - list of strings, the keys you want removed from "d"

    """
    return {x: d[x] for x in d if x not in keys}
