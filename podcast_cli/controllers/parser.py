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
    """
    Takes a URL to a podcast's RSS feed and returns an
    instance of BeautifulSoup, primed with the contents of the
    rss feed and set up to parse XML.

    args:
    url - str, absolute url to the path of an RSS feed

    returns:
    A BeautifulSoup instance set up to parse the contents of the xml file.
    """
    res: requests.models.Response = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(res.text, "xml")
    return soup


def parse_podcast_metadata(soup: BeautifulSoup) -> PodcastType:
    """
    Parses a podcast xml file, through a BeautifulSoup instance, and returns
    the following information:
        - podcast title,
        - podacst description,
        - link to the rss feed,
        - a guid, for identification / tracking purposes.

    args:
    soup - An instance of BeautifulSoup, preferably the output of
        parse_podcast_xml(), but can be any BeautifulSoup instance
        set up to parse a podcast's RSS feed.

    returns:
    PodcastType, a dictionary, containing the keys
        ["title", "description", "link", "guid"]
    """
    channel: Tag = soup.channel
    return PodcastType(
        title=channel.title.text,
        description=channel.description.text,
        link=channel.link.text,
        guid=channel.guid.text
    )


def parse_podcast_episodeset(soup: BeautifulSoup) -> List[EpisodeType]:
    """
    Parses a podcast xml file and returns a list of all the podcast
    episodes it describes.

    It fetches the following information on episodes:
        - title,
        - description,
        - publish date, i.e the date the episode was released.
        - guid, used for tracking / identification purposes,
        - link, a url to the actual episode itself.

    args:
    soup - An instance of BeautifulSoup, preferably the output of
        parse_podcast_xml(), but can be any BeautifulSoup instance
        set up to parse a podcast's RSS feed.

    returns:
    a list of EpisodeType instances (dictionaries), that have the following
    keys:
        - title
        - description
        - pubDate
        - guid
        - link

    """
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
        # NOTE: I realize this might be redundant but I'm doing it anyways.
        #       I refuse to leave sort order to chance.
        key=lambda x: -(x["pubDate"])
    )


def create_podcast_model(podcast: PodcastType) -> PodcastModel:
    """
    A thin wrapper around PodcastModel.create() just so I can annotate
    the function with PodcastModel. .create() will insert a record
    into the database

    args:
    podcast - instance of PodcastType (really just a dictionary) describing
        a podcast.

    returns:
    an instance of PodcastModel, which is a subclass of peewee.Model and
    allows access to the database.
    """
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
    """
    A thin wrapper around EpisodeModel.create() just so I can annotate
    the function with a return type of EpisodeModel. .create() will
    insert a record into the database.

    args:
    parent - instance of PodcastModel, describing a podcast.
    episode - instance of EpisodeType, or any dictionary that has the
        following keys: ["title", "description", "link", "guid"]

    returns:
    an instance of EpisodeModel, which is a subclass of peewee.Model and
    allows access to the database.
    """
    return EpisodeModel.create(
        title=episode["title"],
        description=episode["description"],
        link=episode["link"],
        guid=episode["guid"],
        pubDate=episode["pubDate"],
        podcast=parent
    )


# TODO: Maybe refactor this to take a PodcastModel instead of PodcastType
#       and then re-do the initial view to manaully call the other functions
#       and just pass their output as input into this one?
def insert_to_db(
    podcast: PodcastType,
    episodes: List[EpisodeType]
) -> PodcastEpisodeBundle:
    """
    A helper function that will insert a PodcastModel and all associated
    EpisodeModels into the database.

    args:
    podcast - instance of PodcastType, representing a podcast,
    episodes - a list of EpisodeTypes, representing all the episodes for the
        passed-in podcast.
    """
    parent_model = create_podcast_model(podcast)
    ep_models = [create_podcast_episode(parent_model, ep) for ep in episodes]
    return PodcastEpisodeBundle((parent_model, ep_models))
