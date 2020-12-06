from typing import List
from peewee import ModelObjectCursorWrapper
from podcast_cli.models.database_models import PodcastModel
from podcast_cli.models.custom_types import PodcastType


def __pc_model_to_type(podcast: PodcastModel) -> PodcastType:
    """
    Internal use only, converts a PodcastModel to PodcastType.

    args:
    podcast - PodcastModel, instance of a PodcastModel.

    returns:
    An instance of PodcastType
    """
    return PodcastType(
        pk=podcast.id,
        title=podcast.title,
        description=podcast.description,
        link=podcast.link,
        guid=podcast.guid,
    )


def add_one_podcast(some_podcast: PodcastType) -> PodcastModel:
    """
    Wrapper over PodcastModel.create().

    args:
    some_podcast - dict, REQUIRES the following keys: "title",
        "description", "link", "guid"

    returns:
    An instance of PodcastModel.
    """
    mod: PodcastModel = PodcastModel.create(
        title=some_podcast["title"],
        description=some_podcast["description"],
        link=some_podcast["link"],
        guid=some_podcast["guid"],
    )

    return __pc_model_to_type(mod)


# NOTE: it's worth noting that I could probably hack something
#       together to allow me to search by any arbitrary field
#       but I can't, at the moment, figure out how to do that
#       in a way that won't look terrible.
#       Part of the reason is that Peewee's "query builder" mechanism
#       works by chaining method calls, (and IMO isn't
#       really abstracting much of the SQL away but that's neither
#       here nor there), and I've yet to figure out a clean
#       way to do the "exclusive or" thing properly.
#       For now, I will make it a rule that you will need to
#       provide the id of whatever podcast / episode you want to
#       interact with.
#       Thankfully, the use cases aren't complex enough to require
#       anything more than simple PK search.
def get_one_podcast(pk: int) -> PodcastType:
    podcast: PodcastModel = (
        PodcastModel.get_by_id(pk)
    )

    return __pc_model_to_type(podcast)


def get_all_podcasts() -> List[PodcastType]:
    q: ModelObjectCursorWrapper = (
        PodcastModel.select().execute()
    )

    return [__pc_model_to_type(p) for p in q]
