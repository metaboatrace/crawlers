from datetime import date

from metaboatrace.models.race import RaceInformation as RaceEntity
from metaboatrace.models.stadium import StadiumTelCode
from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.location import (
    create_race_entry_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.scraping import (
    extract_race_entries,
    extract_race_information,
)

from metaboatrace.crawlers.utils import fetch_html_as_io
from metaboatrace.repositories import RaceEntryRepository, RaceRepository


def crawl_race_information_page(stadium_tel_code: int, date: date, race_number: int) -> None:
    url = create_race_entry_page_url(date, StadiumTelCode(stadium_tel_code), race_number)
    html_io = fetch_html_as_io(url)
    race = extract_race_information(html_io)
    race_repository = RaceRepository()
    race_repository.create_or_update(race)

    html_io.seek(0)
    race_entries = extract_race_entries(html_io)
    race_entry_repository = RaceEntryRepository()
    race_entry_repository.create_or_update_many(race_entries)
