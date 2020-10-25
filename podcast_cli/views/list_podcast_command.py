from typing import List, Dict

import click
from tabulate import tabulate
from peewee import Query  # type: ignore
from playhouse.shortcuts import model_to_dict  # type: ignore

from podcast_cli.models.database_models import PodcastModel
from podcast_cli.models.custom_types import PodcastType
from podcast_cli.views.utils import exclude_keys
from podcast_cli.controllers.podcasts import get_all_podcasts


@click.command()
def podcast_list():
    click.echo("Listing all available podcasts")
    # all_casts: Query = PodcastModel.select().execute()
    all_casts: List[PodcastType] = get_all_podcasts()

    # podcasts: List[PodcastModel] = [x for x in all_casts]
    # dict_podcasts: List[Dict] = [model_to_dict(x) for x in podcasts]

    rdy_podcasts: List[Dict] = [
        exclude_keys(item, ["description"])
        for item in all_casts
    ]

    click.echo(tabulate(rdy_podcasts, headers="keys", tablefmt="grid"))
