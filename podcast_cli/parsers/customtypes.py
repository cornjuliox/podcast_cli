from typing import TypedDict

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
