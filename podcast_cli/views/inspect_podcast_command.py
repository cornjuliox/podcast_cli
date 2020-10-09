import click
from tabulate import tabulate
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from podcast_cli.models.database_models import PodcastModel
from podcast_cli.views.utils import exclude_keys


@click.command()
@click.argument("pk")
def podcast_inspect(pk: int):
    try:
        cast: PodcastModel = PodcastModel.get(PodcastModel.id == pk)
    except DoesNotExist:
        click.echo("Podcast with id # {} does not exist!".format(pk))
        return

    dict_cast: dict = model_to_dict(cast)
    filtered_cast: dict = exclude_keys(dict_cast, "description")

    click.echo(tabulate([filtered_cast], headers="keys", tablefmt="grid"))
