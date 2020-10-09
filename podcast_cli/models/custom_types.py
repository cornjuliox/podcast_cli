from typing import TypedDict, List, NewType, Tuple
from podcast_cli.models.database_models import PodcastModel, EpisodeModel

import arrow  # type: ignore


class EpisodeType(TypedDict, total=False):
    pk: str
    title: str
    description: str
    pubDate: arrow.Arrow
    guid: str
    link: str


class PodcastType(TypedDict, total=False):
    pk: str
    title: str
    description: str
    link: str
    guid: str


PodcastEpisodeBundle = NewType(
    "PodcastEpisodeBundle",
    Tuple[PodcastModel, List[EpisodeModel]]
)


class PodcastEpisodeSet(TypedDict):
    pk: PodcastModel
    episodes: List[EpisodeType]
