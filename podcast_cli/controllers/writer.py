from typing import List

from peewee import ModelObjectCursorWrapper  # type: ignore
from podcast_cli.views.utils import get_latest_number
from podcast_cli.models.database_models import EpisodeModel, PodcastModel


# how should this work?
# $ python main.py podcast_dl_latest
# needs to write latest episodes for each podcast to an m3u playlist.
# to support my own personal podcast listening habits.
# it should get the latest episode (singular) for every podcast
# in the database AND create a playlist.
def write_file(filename: str, content: bytes):
    pass
