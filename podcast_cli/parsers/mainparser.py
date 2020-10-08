import requests
import arrow  # type: ignore
from bs4 import BeautifulSoup, ResultSet, Tag  # type: ignore
from typing import List
from podcast_cli.parsers.customtypes import PodcastEpisode, PodcastDescription


# NOTE: So it turns out that all the podcasts I looked at have the same
#       format for their xml feeds - this simplifies things greatly.
#       Assuming (and hoping) that the formats don't change at some point
#       then this should be enough....
class MainPodcastParser():
    def __init__(self, url):
        self.res: requests.models.Response = requests.get(url)
        self.soup: BeautifulSoup = BeautifulSoup(self.res.text, "xml")

    def get_podcast_metadata(self) -> PodcastDescription:
        channel: Tag = self.soup.channel
        return PodcastDescription(
            title=channel.title.text,
            description=channel.description.text,
            link=channel.link.text,
            guid=channel.guid.text
        )

    def extract_details(self, item: Tag) -> PodcastEpisode:
        # Not quite the way I wanted to do it, but its' the only
        # way that seems to work with Mypy
        dateformatstr: str = "ddd, DD MMM YYYY hh:mm:ss Z"
        return PodcastEpisode(
            title=item.title.text,
            description=item.description.text,
            pubDate=arrow.get(item.pubDate.text, dateformatstr).timestamp,
            guid=item.guid.text,
            url=item.enclosure["url"]
        )

    def get(self) -> List[PodcastEpisode]:
        items: ResultSet = self.soup.find_all("item")
        return sorted(
            [self.extract_details(i) for i in items],
            key=lambda x: -(x["pubDate"])
        )
