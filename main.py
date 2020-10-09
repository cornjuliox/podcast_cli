from typing import List, Optional
import json

import click
from tabulate import tabulate
from peewee import Query  # type: ignore

from podcast_cli.parsers.mainparser import MainPodcastParser
from podcast_cli.models.database_models import db, PodcastModel, EpisodeModel
from podcast_cli.parsers.customtypes import (
    PodcastDescription,
    PodcastEpisode,
    PodcastEpisodeSet
)


podcast_mapping = {
    "Planet Money": "https://feeds.npr.org/510289/podcast.xml",
    "Behind The Bastards": "https://feeds.megaphone.fm/behindthebastards",
    "Freakanomics Radio": "https://www.omnycontent.com/d/playlist/aaea4e69-af51-495e-afc9-a9760146922b/14a43378-edb2-49be-8511-ab0d000a7030/d1b9612f-bb1b-4b85-9c0c-ab0d004ab37a/podcast.rss",  # noqa: E501
    "Corecursive Podcast": "https://corecursive.libsyn.com/feed",
}


def query_all_podcasts() -> List[PodcastDescription]:
    def __unpack_podcast(cast: PodcastModel) -> PodcastDescription:
        return PodcastDescription(
            pk=cast.id,
            title=cast.title,
            link=cast.link
        )
    # NOTE: for learning purposes - peewee seems to mimic SQL with its query
    #       structure. Generally speaking, you'd construct "queries" by
    #       chaining method calls on the Models that mimic SQL
    #       and then top it all off with an .execute() at the end. (cont below)
    query: Query = PodcastModel.select().order_by(PodcastModel.title).execute()
    # NOTE: .execute() as a method will take the generated query and return a
    #       database cursor object that represents the results of said query.
    #       the results won't actually be available as Python objects until
    #       you iterate over the cursor. In that way it seems to be "lazy".
    podcasts: List[PodcastDescription] = [
        __unpack_podcast(podcast)
        for podcast in query
    ]
    return podcasts


@click.group()
def cli():
    # NOTE: Until I see evidence to suggest that this is a bad idea, I am going
    #       to put the db connection code here.
    db.connect()
    db.create_tables([PodcastModel, EpisodeModel])


# No positional arguments! explicit actions are the best actions
# CLI ARG: podcast_add - takes a name and a link to an
#       RSS feed / XML file, and creates a Podcast row.
# @click.command()
# @click.argument("name")
# @click.argument("link")
# def podcast_add(name: str, link: str):
#     """
#     Adds a podcast to the database.

#     input:
#     name: str - the name of the podcast.
#     link: str - the link the podcast's RSS feed, which usually an XML file.
#     """
#     click.echo("You're adding a podcast.")
#     while True:
#         click.echo(
#             "You're adding podcast '{}', at link {}.".format(name, link)
#         )
#         val = click.prompt("Is this correct? y/n")
#         if val.lower() == "y":
#             rows: PodcastModel = PodcastModel.create(
#                 title=name,
#                 link=link
#             )
#             # TODO: Maybe reconsider my decision to require the pk as part
#             #       of the usage of MainPodcastParser.
#             #       The fact that I need to create a table row before I can
#             #       use MPP to get the metadata suggests something wrong
#             #       with the way I'm thinking about things...
#             mpp: MainPodcastParser = MainPodcastParser(url=link, pk=rows.id)
#             desc: PodcastDescription = mpp.get_podcast_metadata()
#             # NOTE: In cases of update()s, the .execute() method actually
#             #       executes the SQL and returns the result of the operation
#             #       i.e the number of rows modified.
#             update_query: int = (
#                 PodcastModel.update(
#                     description=desc["description"],
#                     guid=desc["guid"]
#                 )
#                 .where(PodcastModel.id == rows.id)
#                 .execute()
#             )
#             click.echo(
#                 "Successfully updated metadata on {} row"
#                 .format(update_query)
#             )
#             click.echo(
#                 "Successfully added {} podcast to the database"
#                 .format(rows.title)
#             )
#             break
#         else:
#             break
#     return


# CLI ARG: podcast_remove - takes the PK of the podcast in question and
#       removes its entry from the database.
@click.command()
def podcast_remove():
    click.echo("You're removing a podcast.")


# CLI ARG: podcast_list - lists all podcasts currently in the database
#       (names and links only)
@click.command()
def podcast_list():
    click.echo("You're listing all currently stored podcasts.")
    podcasts: List[PodcastDescription] = query_all_podcasts()
    for x in podcasts:
        x["episode_count"] = EpisodeModel.select().where(EpisodeModel.podcast == x['pk']).count()
    # NOTE: click.echo() as opposed to print for proper
    #       cross-terminal compatibility!
    click.echo(tabulate(podcasts, headers="keys", tablefmt="github"))


# CLI ARG: podcast_inspect - takes the PK of a podcast and prints its
#       details out to the command line.
@click.command()
@click.argument("podcast_pk")
def podcast_inspect(podcast_pk):
    click.echo("You're inspecting a single podcast")

    query: Query = PodcastModel.select().where(PodcastModel.id == podcast_pk)
    cast: Optional[PodcastModel] = PodcastModel.get_or_none(query)

    if cast:
        tabledata: dict = {
            "title": cast.title,
            "description": cast.description,
            "link": cast.link
        }
        click.echo(tabulate([tabledata], headers="keys", tablefmt="github"))
    else:
        click.echo("No podcast with that PK found. Check PK and try again.")


# CLI ARG: podcast_init - fetches the full list of podcasts for any newly added
#          podcast. A "newly added" podcast has 0 episodes stored in a db.
#          This is to differentiate between this and the "update" command
#          which is ultimately supposed to only fetch the "latest" episodes
#          from a feed.
@click.command()
def podcast_init():
    def __has_episodes(podcast: PodcastModel) -> bool:
        count = EpisodeModel.select().where(EpisodeModel.podcast == podcast)
        if count > 0:
            return True
        else:
            return False

    # step 1: get all the podcasts stored.
    click.echo("You are now retrieving episodes for newly added podcasts.")
    podcast: List[PodcastModel] = PodcastModel.select().execute()
    # step 2: filter out the ones that have NO episodes stored in the database.
    empty_podcasts: List[PodcastModel] = [
        pc
        for pc in podcast
        if __has_episodes(pc)
    ]
    click.echo(
        f"The following empty podcasts have been found: {[pc.title for pc in empty_podcasts]}\n"
    )
    # step 3: go and get that shit
    parsers: List[MainPodcastParser] = [
        MainPodcastParser(url=pc.link, pk=pc.id)
        for pc in empty_podcasts
    ]
    episodes: List[PodcastEpisodeSet] = [
        parser.get()
        for parser in parsers
    ]
    # step 4: shove that shit into the database.
    # the parent step may be unnecessary....
    masterlist: List[List] = []
    for es in episodes:
        parent = PodcastModel.get_by_id(es["pk"])
        for ep in es["episodes"]:
            click.echo(json.dumps(ep, indent=2))
            click.echo()
            new_ep = EpisodeModel.create(
                title=ep["title"],
                description=ep["description"],
                link=ep["url"],
                guid=ep["guid"],
                pubDate=ep["pubDate"],
                podcast=parent,
            )
            click.echo(
                "Created {}-{} in database".format(new_ep.id, new_ep.title)
            )
            masterlist.append(ep)


# CLI ARG: update - fetches all the latest episodes. Or at least ITS SUPPOSED TO.
@click.command()
def podcast_update():
    click.echo("You're updating all podcast list epsisodes.")
    podcasts: List[PodcastDescription] = query_all_podcasts()
    parsers: List[MainPodcastParser] = [
        MainPodcastParser(url=cast["link"], pk=cast["pk"])
        for cast in podcasts
    ]
    sorted_episode_list: List[PodcastEpisodeSet] = [x.get() for x in parsers]

    for pes in sorted_episode_list:
        parent_podcast: PodcastModel = PodcastModel.get_by_id(pes['pk'])
        click.echo(f"Now sorting episodes for: {parent_podcast.title}")
        for ep in pes['episodes']:
            click.echo("Checking episode: {}".format(ep["title"]))
            checkquery: Query = (
                EpisodeModel.select()
                            .where(EpisodeModel.guid == ep["guid"])
            )
            # NOTE: Optional in this case meaining row can either be an
            # instance of EpisodeModel or None.
            row: Optional[EpisodeModel] = EpisodeModel.get_or_none(checkquery)
            if row is None:
                results: int = EpisodeModel.create(
                    title=ep['title'],
                    description=ep['description'],
                    pubDate=ep['pubDate'],
                    guid=ep['guid'],
                    podcast=parent_podcast,
                    link=ep["url"]
                )
                click.echo(
                    f"Created id#{results} for pk {parent_podcast.id} {parent_podcast.title}"  # noqa: E501
                )
            else:
                click.echo("{} for {} already exists.\n".format(ep["title"], parent_podcast.title))  # noqa: E501
                continue

    # with open('sorted_results.json', 'w') as F:
    #     F.write(json.dumps(sorted_episode_list, indent=2))


# CLI ARG: test - fetches all the episodes and dumps them to a file
#       for inspection just like it does presently.
from podcast_cli.views.add_podcast_command import podcast_add
cli.add_command(podcast_add)
# cli.add_command(podcast_remove)
cli.add_command(podcast_list)
# cli.add_command(podcast_init)
# cli.add_command(podcast_inspect)
# cli.add_command(podcast_update)

if __name__ == "__main__":
    cli()
