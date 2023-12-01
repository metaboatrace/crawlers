from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from metaboatrace.scrapers.official.website.exceptions import DataNotFound

from metaboatrace.handlers.race import (
    RaceHandlerEvent,
    crawl_odds_handler,
    crawl_race_before_information_handler,
    crawl_race_information_handler,
)


@pytest.fixture
def mock_crawl_race_information_page():  # type: ignore
    with patch("metaboatrace.handlers.race.crawl_race_information_page") as mock_func:
        yield mock_func


@pytest.fixture
def mock_crawl_race_before_information_page():  # type: ignore
    with patch("metaboatrace.handlers.race.crawl_race_before_information_page") as mock_func:
        yield mock_func


# 正常系テスト
def test_crawl_race_information_handler_success(
    mock_crawl_race_information_page: MagicMock,
) -> None:
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19", "race_number": 1})
    result = crawl_race_information_handler(event, {})
    assert result == {"success": True}


# 異常系テスト（レース情報が見つからなかった場合）
def test_crawl_race_information_handler_data_not_found(
    mock_crawl_race_information_page: MagicMock,
) -> None:
    mock_crawl_race_information_page.side_effect = DataNotFound()
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19", "race_number": 1})
    result = crawl_race_information_handler(event, {})
    assert result == {"success": False, "errorCode": "RACER_NOT_FOUND"}


# 異常系テスト（引数が不足している場合）
def test_crawl_race_information_handler_missing_parameters() -> None:
    # stadium_tel_code が欠けている
    event = cast(RaceHandlerEvent, {"date": "2023-11-19", "race_number": 1})
    with pytest.raises(ValueError) as excinfo:
        crawl_race_information_handler(event, {})
    assert "stadium_tel_code is missing in the event parameter" in str(excinfo.value)

    # date が欠けている
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "race_number": 1})
    with pytest.raises(ValueError) as excinfo:
        crawl_race_information_handler(event, {})
    assert "date is missing in the event parameter" in str(excinfo.value)

    # race_number が欠けている
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19"})
    with pytest.raises(ValueError) as excinfo:
        crawl_race_information_handler(event, {})
    assert "race_number is missing in the event parameter" in str(excinfo.value)


# 正常系テスト
def test_crawl_race_before_information_handler_success(
    mock_crawl_race_before_information_page: MagicMock,
) -> None:
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19", "race_number": 1})
    result = crawl_race_before_information_handler(event, {})
    assert result == {"success": True}


# 異常系テスト（レース情報が見つからなかった場合）
def test_crawl_race_before_information_handler_data_not_found(
    mock_crawl_race_before_information_page: MagicMock,
) -> None:
    mock_crawl_race_before_information_page.side_effect = DataNotFound()
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19", "race_number": 1})
    result = crawl_race_before_information_handler(event, {})
    assert result == {"success": False, "errorCode": "RACER_NOT_FOUND"}


# 異常系テスト（引数が不足している場合）
def test_crawl_race_before_information_handler_missing_parameters() -> None:
    # stadium_tel_code が欠けている
    event = cast(RaceHandlerEvent, {"date": "2023-11-19", "race_number": 1})
    with pytest.raises(ValueError) as excinfo:
        crawl_race_before_information_handler(event, {})
    assert "stadium_tel_code is missing in the event parameter" in str(excinfo.value)

    # date が欠けている
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "race_number": 1})
    with pytest.raises(ValueError) as excinfo:
        crawl_race_before_information_handler(event, {})
    assert "date is missing in the event parameter" in str(excinfo.value)

    # race_number が欠けている
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19"})
    with pytest.raises(ValueError) as excinfo:
        crawl_race_before_information_handler(event, {})
    assert "race_number is missing in the event parameter" in str(excinfo.value)


@pytest.fixture
def mock_crawl_trifecta_odds_page():  # type: ignore
    with patch("metaboatrace.handlers.race.crawl_trifecta_odds_page") as mock_func:
        yield mock_func


# 正常系テスト
def test_crawl_odds_handler_success(
    mock_crawl_trifecta_odds_page: MagicMock,
) -> None:
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19", "race_number": 1})
    result = crawl_odds_handler(event, {})
    assert result == {"success": True}


# 異常系テスト（オッズ情報が見つからなかった場合）
def test_crawl_odds_handler_data_not_found(
    mock_crawl_trifecta_odds_page: MagicMock,
) -> None:
    mock_crawl_trifecta_odds_page.side_effect = DataNotFound()
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19", "race_number": 1})
    result = crawl_odds_handler(event, {})
    assert result == {"success": False, "errorCode": "RACER_NOT_FOUND"}


# 異常系テスト（引数が不足している場合）
def test_crawl_odds_handler_missing_parameters() -> None:
    # stadium_tel_code が欠けている
    event = cast(RaceHandlerEvent, {"date": "2023-11-19", "race_number": 1})
    with pytest.raises(ValueError) as excinfo:
        crawl_odds_handler(event, {})
    assert "stadium_tel_code is missing in the event parameter" in str(excinfo.value)

    # date が欠けている
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "race_number": 1})
    with pytest.raises(ValueError) as excinfo:
        crawl_odds_handler(event, {})
    assert "date is missing in the event parameter" in str(excinfo.value)

    # race_number が欠けている
    event = cast(RaceHandlerEvent, {"stadium_tel_code": 4, "date": "2023-11-19"})
    with pytest.raises(ValueError) as excinfo:
        crawl_odds_handler(event, {})
    assert "race_number is missing in the event parameter" in str(excinfo.value)
