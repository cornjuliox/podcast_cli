import requests
from requests import Response
from typing import List

from peewee import ModelObjectCursorWrapper  # type: ignore
from podcast_cli.views.utils import get_latest_number
from podcast_cli.models.database_models import EpisodeModel, PodcastModel


def dl_episode(url: str) -> bytes:
    res: Response = requests.get(url)
    return res.content
