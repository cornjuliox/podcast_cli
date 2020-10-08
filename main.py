import click
from tabulate import tabulate

from podcast_cli.parsers.mainparser import MainPodcastParser
from podcast_cli.models import db, PodcastModel, EpisodeModel
from podcast_cli.parsers.customtypes import PodcastDescription, PodcastEpisode

podcast_mapping = {
    "Planet Money": "https://feeds.npr.org/510289/podcast.xml",
    "Behind The Bastards": "https://feeds.megaphone.fm/behindthebastards",
    "Freakanomics Radio": "https://www.omnycontent.com/d/playlist/aaea4e69-af51-495e-afc9-a9760146922b/14a43378-edb2-49be-8511-ab0d000a7030/d1b9612f-bb1b-4b85-9c0c-ab0d004ab37a/podcast.rss",  # noqa: E501
    "Corecursive Podcast": "https://corecursive.libsyn.com/feed",
}


@click.group()
def cli():
    # NOTE: Until I see evidence to suggest that this is a bad idea, I am going
    #       to put the db connection code here.
    db.connect()
    db.create_tables([PodcastModel, EpisodeModel])


# No positional arguments! explicit actions are the best actions
# CLI ARG: podcast_add - takes a name and a link to an
#       RSS feed / XML file, and creates a Podcast row.
@click.command()
@click.argument("name")
@click.argument("link")
def podcast_add(name: str, link: str):
    """
    Adds a podcast to the database.

    input:
    name: str - the name of the podcast.
    link: str - the link the podcast's RSS feed, which usually an XML file.
    """
    click.echo("You're adding a podcast.")
    while True:
        click.echo("You're adding podcast '{}', at link {}.".format(name, link))
        val = click.prompt("Is this correct? y/n")
        if val.lower() == "y":
            rows = PodcastModel.create(
                title=name,
                link=link
            )
            click.echo(
                "Successfully added {} podcast to the database".format(rows)
            )
            break
        else:
            break

    return


# CLI ARG: podcast_remove - takes the PK of the podcast in question and
#       removes its entry from the database.
@click.command()
def podcast_remove():
    click.echo("You're removing a podcast.")


# CLI ARG: podcast_list - lists all podcasts currently in the database
#       (names and links only)
@click.command()
def podcast_list():
    def __unpack_podcast(cast: PodcastModel) -> PodcastDescription:
        return PodcastDescription(
            pk=cast.id,
            title=cast.title,
            link=cast.link
        )

    click.echo("You're listing all currently stored podcasts.")
    query = PodcastModel.select().order_by(PodcastModel.title).execute()
    podcasts = [__unpack_podcast(podcast) for podcast in query]

    # NOTE: click.echo() as opposed to print for proper
    #       cross-terminal compatibility!
    click.echo(tabulate(podcasts, headers="keys", tablefmt="github"))


# CLI ARG: podcast_inspect - takes the PK of a podcast and prints its
#       details out to the command line.
@click.command()
def podcast_inspect():
    click.echo("You're inspecting a single podcast")


# CLI ARG: update - fetches all the latest episodes.
@click.command()
def podcast_update():
    click.echo("You're updating all podcast list epsisodes.")


# CLI ARG: test - fetches all the episodes and dumps them to a file
#       for inspection just like it does presently.
cli.add_command(podcast_add)
cli.add_command(podcast_remove)
cli.add_command(podcast_list)
cli.add_command(podcast_inspect)
cli.add_command(podcast_update)

if __name__ == "__main__":
    # print("connecting to db...")

    # print("podcast scrape starting...")
    # results: Dict = {
    #     k: MainPodcastParser(v).get()
    #     for k, v in podcast_mapping.items()
    # }
    # print("podcast scrape complete!")
    # print("writing output to json...")
    # with open("results.json", "w") as F:
    #     F.write(json.dumps(results, indent=2))
    # print("output write complete!")
    cli()
