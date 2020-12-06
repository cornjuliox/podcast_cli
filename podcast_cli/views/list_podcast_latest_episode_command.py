from typing import List

from tabulate import tabulate
import click

from podcast_cli.models.database_models import PodcastModel
from podcast_cli.models.custom_types import EpisodeType
from podcast_cli.views.utils import get_latest_number


@click.command()
@click.option("--count", default=5, help="Number of episodes per podcast to show.")  # noqa: E501
def podcast_list_latest_episodes(count: int):
    """
    Lists the latest number of (--count) episodes for a given
    podcast. Default is 5 eps per podcast and results are printed
    to console in a table.

    Checks locally, not remote.

    args:
    count - int, defaults to 5, represents how many eps per podcast
        you'd like to see

    returns:
        nothing.
    """
    click.echo("Examining local database.")
    pcs: List[PodcastModel] = PodcastModel.select()

    # NOTE: the goal is to get the first 5 for every podcast.
    eps: List[List[EpisodeType]] = [get_latest_number(pc, count) for pc in pcs]

    for ep in eps:
        click.echo(tabulate(ep, headers="keys", tablefmt="grid"))
