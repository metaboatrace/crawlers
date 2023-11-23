from datetime import datetime
from typing import Any, Dict, TypedDict, Union

from metaboatrace.crawlers.stadium import (
    crawl_events_from_monthly_schedule_page,
    crawl_pre_inspection_information_page,
)
from metaboatrace.repositories import EventRepository


class MonthlyScheduleHandlerEvent(TypedDict, total=False):
    year: int
    month: int


def crawl_monthly_schedule_handler(
    event: MonthlyScheduleHandlerEvent, context: Any
) -> Dict[str, Union[bool, str]]:
    year = event.get("year")
    if year is None:
        raise ValueError("year is missing in the event parameter")
    month = event.get("month")
    if month is None:
        raise ValueError("month is missing in the event parameter")

    try:
        crawl_events_from_monthly_schedule_page(int(year), int(month), EventRepository())
        return {"success": True}
    except Exception as e:
        return {"success": False, "errorCode": "UNKNOWN_ERROR", "errorMessage": f"{e}"}


class EventEntryHandlerEvent(TypedDict, total=False):
    stadium_tel_code: int
    date: str


def crawl_pre_inspection_information_handler(
    event: EventEntryHandlerEvent, context: Any
) -> Dict[str, Union[bool, str]]:
    date_str = event.get("date")
    if date_str is None:
        raise ValueError("date is missing in the event parameter")
    stadium_tel_code = event.get("stadium_tel_code")
    if stadium_tel_code is None:
        raise ValueError("stadium_tel_code is missing in the event parameter")

    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    try:
        crawl_pre_inspection_information_page(stadium_tel_code, date_obj)
        return {"success": True}
    except Exception as e:
        breakpoint()
        return {"success": False, "errorCode": "UNKNOWN_ERROR", "errorMessage": f"{e}"}
