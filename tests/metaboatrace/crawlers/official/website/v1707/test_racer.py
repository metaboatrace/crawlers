from unittest.mock import MagicMock, Mock, patch

import pytest
from metaboatrace.models.racer import Racer

from metaboatrace.crawlers.official.website.v1707.racer import crawl_racer_from_racer_profile_page


@pytest.fixture
def mock_fetch_html_as_io():  # type: ignore
    with patch("metaboatrace.crawlers.official.website.v1707.racer.fetch_html_as_io") as mock_func:
        mock_func.return_value = Mock(spec=["read", "close"])
        yield mock_func


@pytest.fixture
def mock_extract_racer_profile():  # type: ignore
    dummy_racer = Racer(registration_number=77777, last_name="エース", first_name="モーターマン")
    with patch(
        "metaboatrace.crawlers.official.website.v1707.racer.extract_racer_profile"
    ) as mock_func:
        mock_func.return_value = dummy_racer
        yield mock_func


def test_crawl_racer_from_racer_profile_page(
    mock_fetch_html_as_io: MagicMock, mock_extract_racer_profile: MagicMock
) -> None:
    with patch("metaboatrace.repositories.RacerRepository") as MockRepository:
        mock_repo = MockRepository.return_value
        crawl_racer_from_racer_profile_page(77777, mock_repo)
        mock_repo.create_or_update.assert_called_once_with(mock_extract_racer_profile.return_value)
