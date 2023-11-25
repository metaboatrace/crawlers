from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from metaboatrace.scrapers.official.website.exceptions import DataNotFound

from metaboatrace.handlers.racer import Event, crawl_racer_profile_handler


@pytest.fixture
def mock_crawl_racer_from_racer_profile_page():  # type: ignore
    with patch("metaboatrace.handlers.racer.crawl_racer_from_racer_profile_page") as mock_func:
        yield mock_func


# 正常系テスト
def test_crawl_racer_profile_handler_success(
    mock_crawl_racer_from_racer_profile_page: MagicMock,
) -> None:
    event = cast(Event, {"racer_registration_number": 12345})
    result = crawl_racer_profile_handler(event, {})
    assert result == {"success": True}


# 異常系テスト（レーサーが既に引退しているなどの理由で DataNotFound が発生した場合）
def test_crawl_racer_profile_handler_data_not_found(
    mock_crawl_racer_from_racer_profile_page: MagicMock,
) -> None:
    mock_crawl_racer_from_racer_profile_page.side_effect = DataNotFound()
    event = cast(Event, {"racer_registration_number": 12345})
    result = crawl_racer_profile_handler(event, {})
    assert result == {"success": False, "errorCode": "RACER_NOT_FOUND"}


# 異常系テスト（受信データに処理に必要な引数である racer_registration_number がない場合）
def test_crawl_racer_profile_handler_missing_racer_number() -> None:
    event = cast(Event, {})
    with pytest.raises(ValueError) as excinfo:
        crawl_racer_profile_handler(event, {})
    assert str(excinfo.value) == "racer_registration_number is missing in the event parameter"
