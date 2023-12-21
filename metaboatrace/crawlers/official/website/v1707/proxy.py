import urllib.parse
from datetime import date
from typing import Any

from metaboatrace.models.stadium import StadiumTelCode
from metaboatrace.scrapers.official.website.v1707.utils import (
    format_stadium_tel_code_for_query_string,
)

BASE_URL = "http://localhost:55000"
VERSION = "1707"


def create_url(page_type: str, **kwargs: Any) -> str:
    params = {"version": VERSION, "page_type": page_type, **kwargs}
    return f"{BASE_URL}/file?{urllib.parse.urlencode(params)}"


def create_race_entry_page_url(
    race_holding_date: date, stadium_tel_code: StadiumTelCode, race_number: int
) -> str:
    return create_url(
        "race_information_page",
        race_number=race_number,
        stadium_tel_code=format_stadium_tel_code_for_query_string(stadium_tel_code),
        race_opened_on=race_holding_date.strftime("%Y-%m-%d"),
    )


def create_race_before_information_page_url(
    race_holding_date: date, stadium_tel_code: StadiumTelCode, race_number: int
) -> str:
    return create_url(
        "race_exhibition_information_page",
        race_number=race_number,
        stadium_tel_code=format_stadium_tel_code_for_query_string(stadium_tel_code),
        race_opened_on=race_holding_date.strftime("%Y-%m-%d"),
    )


def create_odds_page_url(
    race_holding_date: date, stadium_tel_code: StadiumTelCode, race_number: int
) -> str:
    return create_url(
        "race_odds_page",
        race_number=race_number,
        stadium_tel_code=format_stadium_tel_code_for_query_string(stadium_tel_code),
        race_opened_on=race_holding_date.strftime("%Y-%m-%d"),
    )


def create_race_result_page_url(
    race_holding_date: date, stadium_tel_code: StadiumTelCode, race_number: int
) -> str:
    return create_url(
        "race_result_page",
        race_number=race_number,
        stadium_tel_code=format_stadium_tel_code_for_query_string(stadium_tel_code),
        race_opened_on=race_holding_date.strftime("%Y-%m-%d"),
    )


def create_racer_profile_page_url(racer_registration_number: int) -> str:
    return create_url("racer_profile_page", registration_number=racer_registration_number)


def create_monthly_schedule_page_url(year: int, month: int) -> str:
    return create_url("event_schedule_page", year=year, month=month)


def create_event_entry_page_url(stadium_tel_code: StadiumTelCode, event_starts_on: date) -> str:
    return create_url(
        "event_entries_page",
        stadium_tel_code=format_stadium_tel_code_for_query_string(stadium_tel_code),
        event_starts_on=event_starts_on.strftime("%Y-%m-%d"),
    )


def create_event_holding_page_url(date: date) -> str:
    return create_url("event_holdings_page", date=date.strftime("%Y-%m-%d"))
