import requests
import arrow  # type: ignore
from bs4 import BeautifulSoup, ResultSet, Tag  # type: ignore
from typing import List

from podcast_cli.models.custom_types import (
    PodcastType,
    EpisodeType,
    PodcastEpisodeBundle
)
from podcast_cli.models.database_models import (
    PodcastModel,
    EpisodeModel
)


def parse_podcast_xml(url: str) -> BeautifulSoup:
    res: requests.models.Response = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(res.text, "xml")
    return soup


def parse_podcast_metadata(soup: BeautifulSoup) -> PodcastType:
    channel: Tag = soup.channel
    return PodcastType(
        title=channel.title.text,
        description=channel.description.text,
        link=channel.link.text,
        guid=channel.guid.text
    )


def parse_podcast_episodeset(soup: BeautifulSoup) -> List[EpisodeType]:
    def __extract_details(item: Tag) -> EpisodeType:
        dateformatstr: str = "ddd, DD MMM YYYY hh:mm:ss Z"
        return EpisodeType(
            title=item.title.text,
            description=item.description.text,
            pubDate=arrow.get(item.pubDate.text, dateformatstr).timestamp,
            guid=item.guid.text,
            link=item.enclosure["url"]
        )

    items: ResultSet = soup.find_all("item")
    return sorted(
        [__extract_details(item) for item in items],
        key=lambda x: -(x["pubDate"])
    )


def create_podcast_model(podcast: PodcastType) -> PodcastModel:
    return PodcastModel.create(
        title=podcast["title"],
        description=podcast["description"],
        link=podcast["link"],
        guid=podcast["guid"]
    )


def create_podcast_episode(
    parent: PodcastModel,
    episode: EpisodeType
) -> EpisodeModel:
    return EpisodeModel.create(
        title=episode["title"],
        description=episode["description"],
        link=episode["link"],
        guid=episode["guid"],
        pubDate=episode["pubDate"],
        podcast=parent
    )


def insert_to_db(
    podcast: PodcastType,
    episodes: List[EpisodeType]
) -> PodcastEpisodeBundle:
    parent_model = create_podcast_model(podcast)
    ep_models = [create_podcast_episode(parent_model, ep) for ep in episodes]
    return PodcastEpisodeBundle((parent_model, ep_models))
