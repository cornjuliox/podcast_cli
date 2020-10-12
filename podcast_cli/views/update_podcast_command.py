from typing import Optional, List, Dict

import click
import arrow
from peewee import ModelObjectCursorWrapper
from playhouse.shortcuts import model_to_dict
from bs4 import BeautifulSoup
from tabulate import tabulate

from podcast_cli.models.database_models import (
    PodcastModel,
    EpisodeModel
)
from podcast_cli.models.custom_types import EpisodeType
from podcast_cli.views.utils import exclude_keys
from podcast_cli.controllers.parser import (
    parse_podcast_episodeset,
    parse_podcast_xml
)


def get_timestamp(some_date: str) -> int:
    return arrow.get(some_date).timestamp


def get_latest_episode_remote(podcast: PodcastModel) -> EpisodeType:
    click.echo("Fetching latest episodes for {}".format(podcast.title))
    res: BeautifulSoup = parse_podcast_xml(podcast.link)
    eps: List[EpisodeType] = parse_podcast_episodeset(res)
    sorted_eps: List[EpisodeType] = sorted(
        eps,
        key=lambda x: -(x["pubDate"])
    )
    # NOTE: It's worth noting that I probably could just whip up a
    #       function that only scrapes the first -item- from the XML file
    #       but at this point it strikes me as premature optimization.
    #       On top of that, I'm not sure bs4 will preserve the order it
    #       encounters the items in, so simply taking the first element
    #       might not be accurate.
    return sorted_eps[0]


def get_latest_episode_local(podcast: PodcastModel) -> dict:
    click.echo(
        "Checking latest stored episode for podcast {}".format(podcast.title)
    )
    raw_ep: EpisodeModel = (
        EpisodeModel.select()
                    .where(EpisodeModel.podcast == podcast)
                    .order_by(EpisodeModel.pubDate.desc())
                    .get()
    )

    dict_ep: dict = model_to_dict(raw_ep)
    ep = exclude_keys(dict_ep, ["description", "link"])

    return ep


@click.command()
@click.option("--pk", default=None)
def podcast_update(pk: Optional[int]):
    if pk:
        parent: PodcastModel = PodcastModel.get_by_id(pk)
        click.echo("Checking for new episodes of {}".format(parent.title))

        # NOTE: List[EpisodeType] == List[dict] and
        #       EpisodeType == Dict
        latest_feed: EpisodeType = get_latest_episode_remote(parent)
        latest_local: dict = get_latest_episode_local(parent)
        is_different: bool = latest_feed["guid"] != latest_local["guid"]
        is_more_recent: bool = (
            get_timestamp(latest_feed["pubDate"]) > get_timestamp(latest_local["pubDate"])
        )
        if is_different and is_more_recent:
            click.echo("Found a new episode:")
            click.echo(
                tabulate(
                    [exclude_keys(latest_feed, ["description", "link"])],
                    headers="keys",
                    tablefmt="grid"
                )
            )
            new: EpisodeModel = EpisodeModel.create(
                title=latest_feed["title"],
                guid=latest_feed["guid"],
                description=latest_feed["description"],
                link=latest_feed["link"],
                podcast=parent
            )
            click.echo(
                "Added new episode {} to db with id of {}".format(
                    latest_feed["title"],
                    new.id
                )
            )
        else:
            click.echo("No new episodes found.")

    else:
        parents: ModelObjectCursorWrapper = PodcastModel.select().execute()
        click.echo("Checking all podcasts for new episodes.")
        mapping: dict = {
            parent.id: get_latest_episode_remote(parent)
            for parent in parents
        }
        # click.echo(tabulate(latest_eps, headers="keys", tablefmt="grid"))
