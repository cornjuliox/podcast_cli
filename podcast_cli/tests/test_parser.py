from unittest.mock import patch
from typing import List
import os

import pytest
from bs4 import BeautifulSoup

from podcast_cli.models.custom_types import (
    PodcastType,
    EpisodeType
)
from podcast_cli.controllers.parser import (
    parse_podcast_xml,
    parse_podcast_metadata,
    parse_podcast_episodeset,
)


TEST_XML = os.path.join(os.getcwd(), "test_xml_planet_money.xml")


def test_parse_xml():
    full_path: str = os.path.join(os.getcwd(), "test_xml_planet_money.xml")

    with open(full_path, "r") as F:
        # NOTE: wow this is weird
        class TempObject():
            text = F.read()

        with patch("podcast_cli.controllers.parser.requests.get") as p:
            p.return_value = TempObject()
            soup: BeautifulSoup = parse_podcast_xml("")

            assert isinstance(soup, BeautifulSoup)


def test_parse_podcast_metadata():
    with open(TEST_XML, "r") as F:
        contents: str = F.read()

    soup: BeautifulSoup = BeautifulSoup(contents, "xml")
    metadata: PodcastType = parse_podcast_metadata(soup)

    assert isinstance(metadata, dict)
    assert "title" in metadata.keys()
    assert "description" in metadata.keys()
    assert "link" in metadata.keys()
    assert "guid" in metadata.keys()


def test_parse_podcast_episodeset():
    with open(TEST_XML, "r") as F:
        contents: str = F.read()

    soup: BeautifulSoup = BeautifulSoup(contents, "xml")
    episodeset: List[EpisodeType] = parse_podcast_episodeset(soup)

    assert len(episodeset) != 0
