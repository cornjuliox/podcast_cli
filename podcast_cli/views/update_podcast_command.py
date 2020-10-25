from typing import Optional, List

import click
import arrow                                        # type: ignore
from peewee import ModelObjectCursorWrapper         # type: ignore
from playhouse.shortcuts import model_to_dict       # type: ignore
from bs4 import BeautifulSoup                       # type: ignore
from tabulate import tabulate

from podcast_cli.models.database_models import (
    PodcastModel,
    EpisodeModel
)
from podcast_cli.models.custom_types import EpisodeType
from podcast_cli.views.utils import exclude_keys, prep_ep_for_report
from podcast_cli.controllers.parser import (
    parse_podcast_episodeset,
    parse_podcast_xml
)


def get_timestamp(some_date: str) -> int:
    return arrow.get(some_date).timestamp


def get_latest_episode_remote(podcast: PodcastModel) -> EpisodeType:
    click.echo("Fetching latest episode for {}".format(podcast.title))
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


def get_latest_episode_local(podcast: PodcastModel) -> EpisodeType:
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
    # ep = exclude_keys(dict_ep, ["description", "link"])

    return EpisodeType(
        pk=dict_ep.get("id", None),
        title=dict_ep.get("title", None),
        description=dict_ep.get("description", None),
        pubDate=dict_ep.get("pubDate", None),
        guid=dict_ep.get("guid", None),
        link=dict_ep.get("link", None),
    )


def is_remote_newer(remote: EpisodeType, local: EpisodeType) -> bool:
    r_timestamp: int = get_timestamp(remote["pubDate"])
    l_timestamp: int = get_timestamp(local["pubDate"])

    is_different: bool = remote["guid"] > local["guid"]
    is_more_recent: bool = r_timestamp > l_timestamp

    if is_different and is_more_recent:
        return True
    else:
        return False


# TODO: Split this into two commands
#       "podcast_update_one", and "podcast_update_all"
@click.command()
@click.option("--pk", default=None)
def podcast_update(pk: Optional[int]):
    if pk:
        parent: PodcastModel = PodcastModel.get_by_id(pk)
        click.echo("Checking for new episodes of {}".format(parent.title))

        # NOTE: List[EpisodeType] == List[dict] and
        #       EpisodeType == Dict
        latest_feed: EpisodeType = get_latest_episode_remote(parent)
        latest_local: EpisodeType = get_latest_episode_local(parent)

        if is_remote_newer(latest_feed, latest_local):
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
        # NOTE: what I'm doing might not be obvious here
        #       I'm putting together a list of dicts such that
        #       {"1": <podcast>, "2": <podcast>}
        #       such that key is the pk of the podcast model
        #       and value is the podcast model itself. 1 / 3
        ez_ref: dict = {
            p.id: p
            for p in parents
        }
        # NOTE: The above allows me to create another dict
        #       where the keys are the PK of the podcast
        #       and the value is the latest episode model
        #       {"1": <episode>, "2": <episode>} 2 / 3
        latest_remote_mapping: dict = {
            k[0]: get_latest_episode_remote(k[1])
            for k in ez_ref.items()
        }
        # NOTE: Same as the above, but the source for below
        #       is the locally stored podcasts 3 / 3
        latest_local_mapping: dict = {
            k[0]: get_latest_episode_local(k[1])
            for k in ez_ref.items()
        }
        results: dict = {
            k: v
            for k, v in latest_remote_mapping.items()
            if is_remote_newer(v, latest_local_mapping[k])
        }

        click.echo("Found {} new episodes!".format(len(results)))

        # "assembly"
        db_insert_results: List[EpisodeModel] = [
            EpisodeModel.create(
                title=v["title"],
                description=v["description"],
                pubDate=v["pubDate"],
                link=v["link"],
                guid=v["guid"],
                podcast=ez_ref[k]
            )
            for k, v in results.items()
        ]

        # "reporting"
        pre_report: List[dict] = [
            exclude_keys(model_to_dict(m), ["description", "link"])
            for m in db_insert_results
        ]
        report: List[EpisodeType] = [
            prep_ep_for_report(ep)
            for ep in pre_report
        ]

        click.echo(tabulate(report, headers="keys", tablefmt="grid"))
