from typing import List
from peewee import ModelObjectCursorWrapper
from podcast_cli.models.database_models import EpisodeModel
from podcast_cli.models.custom_types import EpisodeType


def __ep_model_to_type(model: EpisodeModel) -> EpisodeType:
    return EpisodeType(
        title=model.title,
        description=model.description,
        pubDate=model.pubDate,
        link=model.link,
        podcast=model.podcast.title,
    )


def get_one_episode(pk: int) -> EpisodeType:
    ep: EpisodeModel = (
        EpisodeModel.get_by_id(pk)
    )
    return __ep_model_to_type(ep)


def get_all_episodes(parent: int) -> List[EpisodeType]:
    eps: ModelObjectCursorWrapper = (
        EpisodeModel.select().where(EpisodeModel.podcast == parent).execute()
    )
    return [__ep_model_to_type(ep) for ep in eps]
