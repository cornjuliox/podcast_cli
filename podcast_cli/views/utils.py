from typing import List
from peewee import ModelObjectCursorWrapper
from playhouse.shortcuts import model_to_dict   # type: ignore
from podcast_cli.models.database_models import EpisodeModel, PodcastModel


def exclude_keys(d: dict, keys: List[str]):
    """
    Returns a dictionary containing all keys
    except the ones specified in "keys".

    input:
    d - dictionary, any Python dictionary with key+value pairs
    keys - list of strings, the keys you want removed from "d"

    """
    return {x: d[x] for x in d if x not in keys}


def get_latest_number(cast: PodcastModel, max_limit: int) -> List[dict]:
    """
    Will get the latest max_limit of episodes, where max_limit is an int.
    i.e get_latest_number(someCast, 5) will get the latest 5 episodes for
    every podcdast in the database.

    input:
    cast - PodcastModel instance, represents the podcast whose episodes you
        want.
    max_limit - int, number of episodes
    """
    query: ModelObjectCursorWrapper = (
        EpisodeModel.select()
                    .where(EpisodeModel.podcast == cast)
                    .order_by(-EpisodeModel.pubDate)
                    .limit(max_limit)
                    .execute()
    )
    step1: List[dict] = [model_to_dict(x) for x in query]

    # NOTE: model_to_dict includes the entire PodcastModel object
    #       as a sub-object. This will break tabulate(), so I
    #       exclude_keys() and replace it with a new "podcast" key with only
    #       its title.
    step2: List[dict] = [
        exclude_keys(d, ["description", "guid", "link", "podcast"])
        for d in step1
    ]

    for d in step2:
        d["podcast"] = cast.title

    return step2
