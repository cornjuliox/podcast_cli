from typing import List, Dict

import click
from tabulate import tabulate
from peewee import DoesNotExist                     # type: ignore
from peewee import ModelObjectCursorWrapper         # type: ignore
from playhouse.shortcuts import model_to_dict       # type: ignore

from podcast_cli.models.database_models import PodcastModel, EpisodeModel
from podcast_cli.controllers.podcasts import get_one_podcast
from podcast_cli.views.utils import exclude_keys


@click.command()
@click.argument("pk")
def podcast_list_episodes(pk: int):
    try:
        # parent: PodcastModel = PodcastModel.get_by_id(pk)
        # NOTE: the exceptions will bubble up, won't they?
        parent: PodcastModel = get_one_podcast(pk)
        click.echo(
            "Listing all recorded episodes for podcast {}".format(parent["title"])
        )
    except DoesNotExist:
        click.echo("No podcast with that id exists. Check id and try again.")
        return

    # TODO: Write the episode thing getter
    q: ModelObjectCursorWrapper = (
        EpisodeModel.select()
                    .where(EpisodeModel.podcast.id == parent["pk"])
                    .execute()
    )
    raw_episodes: List[EpisodeModel] = [ep for ep in q]

    dict_episodes: List[Dict] = [model_to_dict(ep) for ep in raw_episodes]
    # TODO: refactor this to use the new prep_ep_for_report() function.
    filtered_dict: List[Dict] = [
        exclude_keys(ep, ["description", "podcast", "link", "guid"])
        for ep in dict_episodes
    ]

    click.echo(tabulate(filtered_dict, headers="keys", tablefmt="grid"))
