from typing import List


def exclude_keys(d: dict, keys: List[str]):
    return {x: d[x] for x in d if x not in keys}
