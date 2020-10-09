from typing import List, Dict

import click
from tabulate import tabulate
from peewee import Query
from playhouse.shortcuts import model_to_dict

from podcast_cli.models.database_models import PodcastModel


@click.command()
def podcast_list():
    click.echo("Listing all available podcasts")
    all_casts: Query = PodcastModel.select().execute()

    podcasts: List[PodcastModel] = [x for x in all_casts]
    dict_podcasts: List[Dict] = [model_to_dict(x) for x in podcasts]

    def __exclude_keys(d: dict, keys: List[str]):
        return {x: d[x] for x in d if x not in keys}

    rdy_podcasts: List[Dict] = [
        __exclude_keys(item, ["description"])
        for item in dict_podcasts
    ]

    click.echo(tabulate(rdy_podcasts, headers="keys", tablefmt="grid"))
