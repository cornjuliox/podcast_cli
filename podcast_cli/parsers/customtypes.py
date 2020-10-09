from typing import TypedDict, List, Optional

import arrow  # type: ignore


class PodcastEpisode(TypedDict, total=False):
    pk: str
    title: str
    description: str
    pubDate: arrow.Arrow
    guid: str
    url: str


class PodcastDescription(TypedDict, total=False):
    pk: str
    title: str
    description: str
    link: str
    guid: str


class PodcastEpisodeSet(TypedDict):
    pk: str
    episodes: List[PodcastEpisode]
