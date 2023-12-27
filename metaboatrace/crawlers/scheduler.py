import time
from datetime import date, datetime, timedelta

import pytz
from metaboatrace.models.stadium import EventHoldingStatus, StadiumTelCode

from metaboatrace.crawlers.celery import app
from metaboatrace.crawlers.official.website.v1707.race import (
    crawl_all_race_information_for_date_and_stadiums,
    crawl_race_before_information_page,
    crawl_race_information_page,
    crawl_race_result_page,
    crawl_trifecta_odds_page,
)
from metaboatrace.crawlers.official.website.v1707.racer import crawl_racer_from_racer_profile_page
from metaboatrace.crawlers.official.website.v1707.stadium import (
    crawl_event_holding_page,
    crawl_events_from_monthly_schedule_page,
    crawl_pre_inspection_information_page,
)
from metaboatrace.orm.database import Session
from metaboatrace.orm.models import Race, Racer

jst = pytz.timezone("Asia/Tokyo")

# HACK: @app.task デコレータを関数定義時に適用することが一般的だが、名前空間パッケージを使ってる兼ね合いからかエラーになるのでここでデコレート
app.task(crawl_events_from_monthly_schedule_page)
app.task(crawl_all_race_information_for_date_and_stadiums)
app.task(crawl_race_information_page)
app.task(crawl_race_before_information_page)
app.task(crawl_trifecta_odds_page)
app.task(crawl_race_result_page)


def _generate_identifier_str(
    race_holding_date: date, stadium_tel_code: StadiumTelCode, race_number: int
) -> str:
    return f"{race_holding_date.strftime('%Y%m%d')}{str(stadium_tel_code.value).zfill(2)}{str(race_number).zfill(2)}"


def _generate_crawl_race_task_id(
    func_name: str, race_holding_date: date, stadium_tel_code: StadiumTelCode, race_number: int
) -> str:
    return (
        f"{func_name}_{_generate_identifier_str(race_holding_date, stadium_tel_code, race_number)}"
    )


@app.task
def schedule_crawl_events_from_monthly_schedule_page() -> None:
    now = datetime.now()
    year = now.year
    month = now.month
    crawl_events_from_monthly_schedule_page(year, month)


@app.task
def schedule_crawl_all_race_information_for_today() -> None:
    today = datetime.now(jst).date()
    event_holdings = crawl_event_holding_page(today)
    will_be_opned_event_holdings = [
        e for e in event_holdings if e.status == EventHoldingStatus.OPEN
    ]
    stadium_tel_codes = [e.stadium_tel_code for e in will_be_opned_event_holdings]
    crawl_all_race_information_for_date_and_stadiums(today, stadium_tel_codes)


@app.task
def schedule_crawl_events_starting_today_for_today() -> None:
    today = datetime.now(jst).date()
    event_holdings = crawl_event_holding_page(today)
    events_starting_today = [
        e for e in event_holdings if e.status == EventHoldingStatus.OPEN and e.progress_day == 1
    ]
    for event_holding in events_starting_today:
        crawl_pre_inspection_information_page(event_holding.stadium_tel_code.value, today)
        time.sleep(1)


@app.task
def reserve_crawl_task_for_races_today() -> None:
    try:
        session = Session()
        today = datetime.now(jst).date()

        races_today = session.query(Race).filter(Race.date == today).all()
        if not races_today:
            raise ValueError("No races found for the specified date")

        for race in races_today:
            crawl_race_information_page.apply_async(  # type: ignore
                args=[race.stadium_tel_code, race.date, race.race_number],
                eta=race.betting_deadline_at - timedelta(minutes=15),
                task_id=_generate_crawl_race_task_id(
                    crawl_race_information_page.__name__,
                    race.date,
                    race.stadium_tel_code,
                    race.race_number,
                ),
            )
            crawl_race_before_information_page.apply_async(  # type: ignore
                args=[race.stadium_tel_code, race.date, race.race_number],
                eta=race.betting_deadline_at - timedelta(minutes=10),
                task_id=_generate_crawl_race_task_id(
                    crawl_race_before_information_page.__name__,
                    race.date,
                    race.stadium_tel_code,
                    race.race_number,
                ),
            )
            crawl_trifecta_odds_page.apply_async(  # type: ignore
                args=[race.stadium_tel_code, race.date, race.race_number],
                eta=race.betting_deadline_at - timedelta(minutes=5),
                task_id=_generate_crawl_race_task_id(
                    crawl_trifecta_odds_page.__name__,
                    race.date,
                    race.stadium_tel_code,
                    race.race_number,
                ),
            )
            crawl_race_result_page.apply_async(  # type: ignore
                args=[race.stadium_tel_code, race.date, race.race_number],
                eta=race.betting_deadline_at + timedelta(minutes=10),
                task_id=_generate_crawl_race_task_id(
                    crawl_race_result_page.__name__,
                    race.date,
                    race.stadium_tel_code,
                    race.race_number,
                ),
            )
    finally:
        session.close()


@app.task
def enqueue_incomplete_racer_crawling() -> None:
    session = Session()
    try:
        incomplete_racers = session.query(Racer).filter(Racer.status == None).limit(3).all()

        racer_registration_numbers = [racer.registration_number for racer in incomplete_racers]

        for registration_number in racer_registration_numbers:
            crawl_racer_from_racer_profile_page(int(registration_number))

    finally:
        session.close()
