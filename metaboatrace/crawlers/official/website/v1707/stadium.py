from datetime import date

from metaboatrace.models.racer import Racer
from metaboatrace.models.stadium import Event, EventHolding, MotorRenewal, StadiumTelCode
from metaboatrace.scrapers.official.website.v1707.pages.event_holding_page.scraping import (
    extract_event_holdings,
)
from metaboatrace.scrapers.official.website.v1707.pages.monthly_schedule_page.scraping import (
    extract_events,
)
from metaboatrace.scrapers.official.website.v1707.pages.pre_inspection_information_page.scraping import (
    extract_event_entries,
    extract_racers,
)

from metaboatrace.crawlers.official.website.v1707.proxy import (
    create_event_entry_page_url,
    create_event_holding_page_url,
    create_monthly_schedule_page_url,
)
from metaboatrace.crawlers.utils import fetch_html_as_io
from metaboatrace.repositories import EventRepository, MotorRenewalRepository, RacerRepository


def crawl_events_from_monthly_schedule_page(
    year: int, month: int, repository: EventRepository = EventRepository()
) -> None:
    url = create_monthly_schedule_page_url(year, month)
    html_io = fetch_html_as_io(url)
    events: list[Event] = extract_events(html_io)
    repository.create_or_update_many(events)


def crawl_pre_inspection_information_page(
    stadium_tel_code: int, date: date, racer_repository: RacerRepository = RacerRepository()
) -> None:
    url = create_event_entry_page_url(StadiumTelCode(stadium_tel_code), date)
    html_io = fetch_html_as_io(url)

    racers: list[Racer] = extract_racers(html_io)
    racer_repository.create_or_update_many(racers)

    html_io.seek(0)
    event_entries = extract_event_entries(html_io)
    if all([ee.quinella_rate_of_motor == 0 for ee in event_entries]):
        motor_renewal_repository = MotorRenewalRepository()
        motor_renewal_repository.create_or_update(
            MotorRenewal(stadium_tel_code=stadium_tel_code, date=date)
        )


# TODO: インターフェースが他と明らかに不揃いなのでメソッド名を変えるかなんかして対応
def crawl_event_holding_page(date: date) -> list[EventHolding]:
    url = create_event_holding_page_url(date)
    html_io = fetch_html_as_io(url)
    return extract_event_holdings(html_io)
