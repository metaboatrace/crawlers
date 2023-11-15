from metaboatrace.models.stadium import Event
from metaboatrace.scrapers.official.website.v1707.pages.monthly_schedule_page.location import (
    create_monthly_schedule_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.monthly_schedule_page.scraping import (
    extract_events,
)

from metaboatrace.crawlers.utils import fetch_html_as_io
from metaboatrace.repositories import EventRepository


def crawl_events_from_monthly_schedule_page(
    year: int, month: int, repository: EventRepository
) -> None:
    url = create_monthly_schedule_page_url(year, month)
    html_io = fetch_html_as_io(url)
    events: list[Event] = extract_events(html_io)
    repository.create_or_update_many(events)
