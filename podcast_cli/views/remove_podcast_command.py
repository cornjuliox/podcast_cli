import click
from peewee import DoesNotExist  # type: ignore
from podcast_cli.models.database_models import PodcastModel


@click.command()
@click.argument("pk")
def podcast_remove(pk: int):
    # NOTE: I could almost swear there was an easier way to do this.
    try:
        pc: PodcastModel = PodcastModel.get_by_id(pk)
        click.echo("Podcast {} - {}".format(pk, pc.title))
        click.echo("Warning! Deleting this podcast entry will remove all of its episode listings locally as well!")   # noqa: E501
    except DoesNotExist:
        click.echo("Podcast with id {} does not exist.".format(pk))
        return

    while True:
        choice: str = click.prompt("Delete this podcast? Y/n")
        if choice.lower() == 'y':
            pc.delete_instance(recursive=True)
            click.echo("Podcast has been deleted, and all episodes removed.")
            break
        elif choice.lower() == 'n':
            click.echo("Exiting.")
            break

    return
