from typing import Any, Dict, TypedDict, Union

from metaboatrace.scrapers.official.website.exceptions import DataNotFound

from metaboatrace.crawlers.racer import crawl_racer_from_racer_profile_page
from metaboatrace.repositories import RacerRepository


class Event(TypedDict, total=False):
    racer_registration_number: int


def crawl_racer_profile_handler(event: Event, context: Any) -> Dict[str, Union[bool, str]]:
    number = event.get("racer_registration_number")
    if number is None:
        raise ValueError("racer_registration_number is missing in the event data")
    racer_registration_number = int(number)

    try:
        repo = RacerRepository()
        crawl_racer_from_racer_profile_page(racer_registration_number, repo)
        return {"success": True}
    except DataNotFound as e:
        return {"success": False, "errorCode": "RACER_NOT_FOUND"}
