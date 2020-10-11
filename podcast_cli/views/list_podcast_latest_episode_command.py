from typing import List

from tabulate import tabulate
import click

from podcast_cli.models.database_models import PodcastModel
from podcast_cli.views.utils import get_latest_number


@click.command()
@click.option("--count", default=5, help="Number of episodes per podcast to show.")  # noqa: E501
def podcast_list_latest_episodes(count: int):
    pcs: List[PodcastModel] = PodcastModel.select()

    # NOTE: the goal is to get the first 5 for every podcast.
    eps: List[List[dict]] = [get_latest_number(pc, count) for pc in pcs]

    for ep in eps:
        click.echo(tabulate(ep, headers="keys", tablefmt="grid"))
