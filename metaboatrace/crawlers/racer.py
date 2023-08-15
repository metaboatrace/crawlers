from injector import inject
from metaboatrace.models.racer import Racer
from metaboatrace.scrapers.official.website.v1707.pages.racer.profile_page.location import (
    create_racer_profile_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.racer.profile_page.scraping import (
    extract_racer_profile,
)

from metaboatrace.crawlers.utils import fetch_html_as_io
from metaboatrace.repositories import RacerRepository


@inject
def crawl_racer_from_racer_profile_page(
    racer_registration_number: int, repository: RacerRepository
) -> None:
    url = create_racer_profile_page_url(racer_registration_number)
    html_io = fetch_html_as_io(url)
    racer: Racer = extract_racer_profile(html_io)
    repository.create_or_update(racer)
