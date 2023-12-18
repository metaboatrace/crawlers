import time
from datetime import datetime

from metaboatrace.models.stadium import EventHoldingStatus

from metaboatrace.crawlers.celery import app
from metaboatrace.crawlers.official.website.v1707.race import (
    crawl_all_race_information_for_date_and_stadiums,
)
from metaboatrace.crawlers.official.website.v1707.racer import crawl_racer_from_racer_profile_page
from metaboatrace.crawlers.official.website.v1707.stadium import (
    crawl_event_holding_page,
    crawl_events_from_monthly_schedule_page,
    crawl_pre_inspection_information_page,
)
from metaboatrace.orm.database import Session
from metaboatrace.orm.models import Racer

# HACK: @app.task デコレータを関数定義時に適用することが一般的だが、名前空間パッケージを使ってる兼ね合いからかエラーになるのでここでデコレート
app.task(crawl_events_from_monthly_schedule_page)
app.task(crawl_all_race_information_for_date_and_stadiums)


@app.task
def schedule_crawl_events_from_monthly_schedule_page() -> None:
    now = datetime.now()
    year = now.year
    month = now.month
    crawl_events_from_monthly_schedule_page(year, month)


@app.task
def schedule_crawl_all_race_information_for_today() -> None:
    date = datetime.today()
    event_holdings = crawl_event_holding_page(date)
    will_be_opned_event_holdings = [
        e for e in event_holdings if e.status == EventHoldingStatus.OPEN
    ]
    stadium_tel_codes = [e.stadium_tel_code for e in will_be_opned_event_holdings]
    crawl_all_race_information_for_date_and_stadiums(date, stadium_tel_codes)


@app.task
def schedule_crawl_events_starting_today_for_today() -> None:
    date = datetime.today()
    event_holdings = crawl_event_holding_page(date)
    events_starting_today = [
        e for e in event_holdings if e.status == EventHoldingStatus.OPEN and e.progress_day == 1
    ]
    for event_holding in events_starting_today:
        crawl_pre_inspection_information_page(event_holding.stadium_tel_code.value, date)
        time.sleep(1)


@app.task
def enqueue_incomplete_racer_crawling() -> None:
    session = Session()
    try:
        incomplete_racers = session.query(Racer).filter(Racer.last_name == "").limit(3).all()

        for racer in incomplete_racers:
            crawl_racer_from_racer_profile_page(int(racer.registration_number))
    finally:
        session.close()
