from typing import List, Dict

import click
from tabulate import tabulate
from bs4 import BeautifulSoup
from playhouse.shortcuts import model_to_dict
from peewee import DoesNotExist

from podcast_cli.controllers.parser import (
    parse_podcast_xml,
    parse_podcast_metadata,
    parse_podcast_episodeset,
    insert_to_db
)
from podcast_cli.models.custom_types import (
    PodcastType,
    PodcastEpisodeBundle,
    EpisodeType
)
from podcast_cli.models.database_models import PodcastModel

# from tabulate import tabulate
# from peewee import Query  # type: ignore

# from typing import List, Optional
# import json


# V2 of the podcast_add command will take the URL and grab
# the podcast name and metadata out.
@click.command()
@click.argument("url")
def podcast_add(url: str):
    soup: BeautifulSoup = parse_podcast_xml(url)
    cast: PodcastType = parse_podcast_metadata(soup)

    # NOTE: This is a guard to ensure that podcasts don't get added twice
    try:
        PodcastModel.get(PodcastModel.guid == cast["guid"])
        click.echo("This podcast already exists in our system!")
        return
    except DoesNotExist:
        pass

    # NOTE: I've decided i want the link to be to the rss feed and not
    # to the homepage. The override is out here.
    cast["link"]: str = url
    episodes: List[EpisodeType] = parse_podcast_episodeset(soup)

    bundle: PodcastEpisodeBundle = insert_to_db(cast, episodes)
    parent: Dict = model_to_dict(bundle[0])

    episodes: List[Dict] = [model_to_dict(ep) for ep in bundle[1]]

    # NOTE: printing large bodies of text through tabulate breaks it
    #       in terrible ways. to mitigate this I will
    #       exclude them selectively, manually.
    podcastoutput: dict = {
        k: parent[k]
        for k in ["title", "link", "guid"]
    }

    podcastoutput["episode_count"] = len(episodes)
    click.echo("Below is a summary of the podcasts added")
    click.echo(tabulate([podcastoutput], headers="keys", tablefmt="grid"))
