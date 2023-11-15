from typing import Any, Dict, cast
from unittest.mock import MagicMock, patch

import pytest

from metaboatrace.handlers.stadium_handler import Event, crawl_monthly_schedule_handler


@pytest.fixture
def mock_crawl_events_from_monthly_schedule_page():
    with patch(
        "metaboatrace.handlers.stadium_handler.crawl_events_from_monthly_schedule_page"
    ) as mock_func:
        yield mock_func


def test_crawl_monthly_schedule_handler_success(
    mock_crawl_events_from_monthly_schedule_page: MagicMock,
):
    event = cast(Event, {"year": 2021, "month": 5})
    result = crawl_monthly_schedule_handler(event, {})
    assert result == {"success": True}


def test_crawl_monthly_schedule_handler_failure(
    mock_crawl_events_from_monthly_schedule_page: MagicMock,
):
    mock_crawl_events_from_monthly_schedule_page.side_effect = Exception("error occurred")
    event = cast(Event, {"year": 2021, "month": 5})
    result = crawl_monthly_schedule_handler(event, {})
    assert result == {
        "success": False,
        "errorCode": "UNKNOWN_ERROR",
        "errorMessage": "error occurred",
    }


def test_crawl_monthly_schedule_handler_missing_parameters():
    event = cast(Event, {"year": 2021})  # month が欠けている
    with pytest.raises(ValueError) as excinfo:
        crawl_monthly_schedule_handler(event, {})
    assert "month is missing in the event parameter" in str(excinfo.value)
