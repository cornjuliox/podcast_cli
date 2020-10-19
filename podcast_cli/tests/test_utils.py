from unittest.mock import patch
from typing import List
import os

import pytest

from podcast_cli.views.utils import exclude_keys, prep_ep_for_report
from podcast_cli.models.custom_types import EpisodeType


def test_exlclude_keys():
    some_dict = {
        "key1": 0,
        "key2": 1,
        "key3": 2,
        "key4": 3,
        "key5": 4,
    }

    new_dict = exclude_keys(some_dict, ["key2", "key3", "key10"])

    assert "key2" not in new_dict
    assert "key3" not in new_dict


def test_prep_ep():
    podcast: dict = {
        "pk": 25,
        "title": "Test Podcast 1",
        "description": "Hello World One Two Three",
        "link": "https://www.google.com",
        "guid": "abcd-efgh-lkc-12345",
        "pubDate": 1603002506,
        "podcast": {"title": "Planet Money"},
    }

    new_cast: EpisodeType = prep_ep_for_report(podcast)

    assert "description" not in new_cast.keys()
    assert "link" not in new_cast.keys()
