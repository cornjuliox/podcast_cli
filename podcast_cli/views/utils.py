from typing import List, Mapping

import arrow
from peewee import ModelObjectCursorWrapper     # type: ignore
from playhouse.shortcuts import model_to_dict   # type: ignore

from podcast_cli.models.database_models import EpisodeModel, PodcastModel


# NOTE: This folder will house functions that can be used across
#       multiple places in the project, and not just in one specific area.


def exclude_keys(d: Mapping, keys: List[str]):
    """
    Returns a dictionary containing all keys
    except the ones specified in "keys".

    input:
    d - dictionary, any Python dictionary with key+value pairs
    keys - list of strings, the keys you want removed from "d"

    returns:
    a dict excluding the keys passed in.
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

    return:
    a list of dicts representing podcast episodes, suitable for use with
    tabulate()
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
        prep_ep_for_report(d)
        for d in step1
    ]

    return step2


# NOTE: might turn this into a general utility...
def prep_ep_for_report(episode: dict) -> dict:
    """
    Helper function to prep model_to_dict(EpisodeModel())
    for use with tabulate(). It removes the "link", "description",
    and "podcast" keys.

    It will replace the "podcast" key with the podcast title as
    opposed to the full sub object.

    Finally, it will take the unix timestamp in pubDate, convert it
    to datetime, str() it, and shift it to the local timezone via .local()

    args:
    episode - dict, specifically the output of model_to_dict(EpisodeModel())

    returns:
    a dict missing the "link" and "description" keys, "podcast" replaced
    with podcast.title, and the date humanized and localized.
    """
    episode["podcast"] = episode["podcast"]["title"]
    new_ep = exclude_keys(episode, ["link", "description"])
    new_ep["pubDate"] = str(arrow.get(new_ep["pubDate"]).to("local").datetime)
    return new_ep
