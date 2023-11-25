from typing import Any, Dict, cast
from unittest.mock import MagicMock, patch

import pytest

from metaboatrace.handlers.stadium import (
    EventEntryHandlerEvent,
    MonthlyScheduleHandlerEvent,
    crawl_monthly_schedule_handler,
    crawl_pre_inspection_information_handler,
)


@pytest.fixture
def mock_crawl_events_from_monthly_schedule_page() -> None:
    with patch(
        "metaboatrace.handlers.stadium.crawl_events_from_monthly_schedule_page"
    ) as mock_func:
        yield mock_func


def test_crawl_monthly_schedule_handler_success(
    mock_crawl_events_from_monthly_schedule_page: MagicMock,
) -> None:
    event = cast(MonthlyScheduleHandlerEvent, {"year": 2021, "month": 5})
    result = crawl_monthly_schedule_handler(event, {})
    assert result == {"success": True}


def test_crawl_monthly_schedule_handler_failure(
    mock_crawl_events_from_monthly_schedule_page: MagicMock,
) -> None:
    mock_crawl_events_from_monthly_schedule_page.side_effect = Exception("error occurred")
    event = cast(MonthlyScheduleHandlerEvent, {"year": 2021, "month": 5})
    result = crawl_monthly_schedule_handler(event, {})
    assert result == {
        "success": False,
        "errorCode": "UNKNOWN_ERROR",
        "errorMessage": "error occurred",
    }


def test_crawl_monthly_schedule_handler_missing_parameters() -> None:
    event = cast(MonthlyScheduleHandlerEvent, {"year": 2021})  # month が欠けている
    with pytest.raises(ValueError) as excinfo:
        crawl_monthly_schedule_handler(event, {})
    assert "month is missing in the event parameter" in str(excinfo.value)


@pytest.fixture
def mock_crawl_pre_inspection_information_page() -> None:
    with patch("metaboatrace.handlers.stadium.crawl_pre_inspection_information_page") as mock_func:
        yield mock_func


def test_crawl_pre_inspection_information_handler_success(
    mock_crawl_pre_inspection_information_page: MagicMock,
) -> None:
    event = cast(EventEntryHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19"})
    result = crawl_pre_inspection_information_handler(event, {})
    assert result == {"success": True}


def test_crawl_pre_inspection_information_handler_failure(
    mock_crawl_pre_inspection_information_page: MagicMock,
) -> None:
    mock_crawl_pre_inspection_information_page.side_effect = Exception("error occurred")
    event = cast(EventEntryHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19"})
    result = crawl_pre_inspection_information_handler(event, {})
    assert result == {
        "success": False,
        "errorCode": "UNKNOWN_ERROR",
        "errorMessage": "error occurred",
    }


def test_crawl_pre_inspection_information_handler_missing_parameters() -> None:
    # stadium_tel_code が欠けているケース
    event = cast(EventEntryHandlerEvent, {"date": "2023-11-19"})
    with pytest.raises(ValueError) as excinfo:
        crawl_pre_inspection_information_handler(event, {})
    assert "stadium_tel_code is missing in the event parameter" in str(excinfo.value)

    # date が欠けているケース
    event = cast(EventEntryHandlerEvent, {"stadium_tel_code": 4})
    with pytest.raises(ValueError) as excinfo:
        crawl_pre_inspection_information_handler(event, {})
    assert "date is missing in the event parameter" in str(excinfo.value)
