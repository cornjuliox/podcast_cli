import click

from podcast_cli.models.database_models import PodcastModel, EpisodeModel, db
from podcast_cli.views.add_podcast_command import podcast_add
from podcast_cli.views.list_podcast_command import podcast_list
from podcast_cli.views.remove_podcast_command import podcast_remove
from podcast_cli.views.inspect_podcast_command import podcast_inspect


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


cli.add_command(podcast_add)
cli.add_command(podcast_remove)
cli.add_command(podcast_list)
cli.add_command(podcast_inspect)

if __name__ == "__main__":
    cli()
