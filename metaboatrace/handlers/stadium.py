from datetime import datetime
from typing import Any, Dict, TypedDict, Union

from metaboatrace.crawlers.stadium import crawl_events_from_monthly_schedule_page
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
