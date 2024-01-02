import time
from datetime import date, datetime, timedelta

import pytz
from metaboatrace.models.stadium import EventHoldingStatus
from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled

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
from metaboatrace.repositories import RaceRepository, RacerRepository

jst = pytz.timezone("Asia/Tokyo")


def _generate_identifier_str(
    race_holding_date: date, stadium_tel_code: int, race_number: int
) -> str:
    # note: ORM のモデルの属性を引数に使うので、 stadium_tel_code は int
    return f"{race_holding_date.strftime('%Y%m%d')}{str(stadium_tel_code).zfill(2)}{str(race_number).zfill(2)}"


def _generate_crawl_race_task_id(
    func_name: str, race_holding_date: date, stadium_tel_code: int, race_number: int
) -> str:
    return (
        f"{func_name}_{_generate_identifier_str(race_holding_date, stadium_tel_code, race_number)}"
    )


def _revoke_future_race_tasks(
    stadium_tel_code: int, race_opened_on: date, start_race_number: int
) -> None:
    tasks = [
        crawl_race_information_page,
        crawl_race_before_information_page,
        crawl_trifecta_odds_page,
        crawl_race_result_page,
    ]

    for n in range(start_race_number, 13):
        for task in tasks:
            task_id = _generate_crawl_race_task_id(
                task.__name__, race_opened_on, stadium_tel_code, n
            )
            app.control.revoke(task_id, terminate=True)


@app.task(bind=True)
def _race_task_failure_handler(self, exc, task_id, args, kwargs, einfo):  # type: ignore
    if isinstance(exc, RaceCanceled):
        stadium_tel_code, race_opened_on, race_number = args

        repository = RaceRepository()
        repository.cancel(stadium_tel_code, race_opened_on, race_number)

        _revoke_future_race_tasks(stadium_tel_code, race_opened_on, race_number)
    else:
        raise exc


def _schedule_race_tasks(race: Race, tasks_with_timedelta) -> None:  # type: ignore
    for task_func, delta in tasks_with_timedelta:
        eta = race.betting_deadline_at + delta
        task_func.apply_async(
            args=[race.stadium_tel_code, race.date, race.race_number],
            eta=eta,
            task_id=_generate_crawl_race_task_id(
                task_func.__name__,
                race.date,  # type: ignore
                race.stadium_tel_code,  # type: ignore
                race.race_number,  # type: ignore
            ),
            link_error=_race_task_failure_handler.s(),
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

        tasks_with_timedelta = [
            (crawl_race_information_page, timedelta(minutes=-15)),
            (crawl_race_before_information_page, timedelta(minutes=-10)),
            (crawl_trifecta_odds_page, timedelta(minutes=-5)),
            (crawl_race_result_page, timedelta(minutes=20)),
        ]

        for race in races_today:
            _schedule_race_tasks(race, tasks_with_timedelta)
    finally:
        session.close()


@app.task
def enqueue_incomplete_racer_crawling() -> None:
    session = Session()
    try:
        incomplete_racers = session.query(Racer).filter(Racer.status == None).limit(3).all()

        racer_registration_numbers = [racer.registration_number for racer in incomplete_racers]

        for registration_number in racer_registration_numbers:
            try:
                crawl_racer_from_racer_profile_page(int(registration_number))
            except DataNotFound:
                repository = RacerRepository()
                repository.make_retired(registration_number)  # type: ignore

    finally:
        session.close()
