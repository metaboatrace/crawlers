from datetime import datetime
from typing import Any, Dict, TypedDict, Union

from metaboatrace.scrapers.official.website.exceptions import DataNotFound

from metaboatrace.crawlers.race import (
    crawl_race_before_information_page,
    crawl_race_information_page,
    crawl_race_result_page,
    crawl_trifecta_odds_page,
)


class RaceHandlerEvent(TypedDict, total=False):
    stadium_tel_code: int
    date: str
    race_number: int


def extract_parameters_from_event(event: RaceHandlerEvent) -> tuple[int, datetime.date, int]:
    stadium_tel_code = event.get("stadium_tel_code")
    if stadium_tel_code is None:
        raise ValueError("stadium_tel_code is missing in the event parameter")

    date_str = event.get("date")
    if date_str is None:
        raise ValueError("date is missing in the event parameter")
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    race_number = event.get("race_number")
    if race_number is None:
        raise ValueError("race_number is missing in the event parameter")

    return stadium_tel_code, date_obj, int(race_number)


def crawl_race_information_handler(
    event: RaceHandlerEvent, context: Any
) -> Dict[str, Union[bool, str]]:
    stadium_tel_code, date_obj, race_number = extract_parameters_from_event(event)

    try:
        crawl_race_information_page(stadium_tel_code, date_obj, race_number)
        return {"success": True}
    except DataNotFound as e:
        return {"success": False, "errorCode": "RACER_NOT_FOUND"}


def crawl_race_before_information_handler(
    event: RaceHandlerEvent, context: Any
) -> Dict[str, Union[bool, str]]:
    stadium_tel_code, date_obj, race_number = extract_parameters_from_event(event)

    try:
        crawl_race_before_information_page(stadium_tel_code, date_obj, race_number)
        return {"success": True}
    except DataNotFound as e:
        return {"success": False, "errorCode": "RACER_NOT_FOUND"}


def crawl_odds_handler(event: RaceHandlerEvent, context: Any) -> Dict[str, Union[bool, str]]:
    stadium_tel_code, date_obj, race_number = extract_parameters_from_event(event)

    try:
        crawl_trifecta_odds_page(stadium_tel_code, date_obj, race_number)
        return {"success": True}
    except DataNotFound as e:
        # TODO: ここではレース中止系の例外を拾うのが正解（他のハンドラでも同様）
        return {"success": False, "errorCode": "RACER_NOT_FOUND"}


def crawl_race_result_handler(event: RaceHandlerEvent, context: Any) -> Dict[str, Union[bool, str]]:
    stadium_tel_code, date_obj, race_number = extract_parameters_from_event(event)

    try:
        crawl_race_result_page(stadium_tel_code, date_obj, race_number)
        return {"success": True}
    except DataNotFound as e:
        return {"success": False, "errorCode": "RACER_NOT_FOUND"}
