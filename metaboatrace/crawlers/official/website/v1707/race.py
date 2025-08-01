import time
from datetime import date

from metaboatrace.crawlers.celery import app
from metaboatrace.crawlers.exceptions import IncompleteDataError, RaceDeadlineChanged
from metaboatrace.crawlers.utils import fetch_html_as_io
from metaboatrace.models.race import BoatSetting, RaceEntry
from metaboatrace.models.stadium import StadiumTelCode
from metaboatrace.repositories import (
    BoatBettingContributeRateAggregationRepository,
    BoatSettingRepository,
    CircumferenceExhibitionRecordRepository,
    DisqualifiedRaceEntryRepository,
    MotorBettingContributeRateAggregationRepository,
    MotorMaintenanceRepository,
    OddsRepository,
    PayoffRepository,
    RaceEntryRepository,
    RacerConditionRepository,
    RaceRecordRepository,
    RaceRepository,
    RacerWinningRateAggregationRepository,
    StartExhibitionRecordRepository,
    WeatherConditionRepository,
    WinningRaceEntryRepository,
)
from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled
from metaboatrace.scrapers.official.website.v1707.pages.race.before_information_page.location import (
    create_race_before_information_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.before_information_page.scraping import (
    extract_boat_settings,
    extract_circumference_exhibition_records,
    extract_racer_conditions,
    extract_start_exhibition_records,
    extract_weather_condition,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.location import (
    create_race_entry_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.scraping import (
    extract_boat_performances,
    extract_motor_performances,
    extract_race_entries,
    extract_race_information,
    extract_racer_performances,
    is_deadline_changed,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.odds.trifecta_page.location import (
    create_odds_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.odds.trifecta_page.scraping import (
    extract_odds,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.result_page.location import (
    create_race_result_page_url,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.result_page.scraping import (
    extract_race_payoffs,
    extract_race_records,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.result_page.scraping import (
    extract_weather_condition as extract_weather_condition_in_performance,
)


def _create_boat_setting_from(race_entry: RaceEntry) -> BoatSetting:
    return BoatSetting(
        race_holding_date=race_entry.race_holding_date,
        stadium_tel_code=race_entry.stadium_tel_code,
        race_number=race_entry.race_number,
        pit_number=race_entry.pit_number,
        boat_number=race_entry.boat_number,
        motor_number=race_entry.motor_number,
        motor_parts_exchanges=[],
    )


@app.task
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

    html_io.seek(0)
    boat_settings = [_create_boat_setting_from(race_entry) for race_entry in race_entries]
    boat_setting_repository = BoatSettingRepository()
    boat_setting_repository.create_or_update_many(boat_settings, ["boat_number", "motor_number"])

    html_io.seek(0)
    boat_performances = extract_boat_performances(html_io)
    boat_betting_contribute_rate_aggregation_repository = (
        BoatBettingContributeRateAggregationRepository()
    )
    boat_betting_contribute_rate_aggregation_repository.create_or_update_many(boat_performances)

    html_io.seek(0)
    motor_performances = extract_motor_performances(html_io)
    motor_betting_contribute_rate_aggregation_repository = (
        MotorBettingContributeRateAggregationRepository()
    )
    motor_betting_contribute_rate_aggregation_repository.create_or_update_many(motor_performances)

    html_io.seek(0)
    racer_performances = extract_racer_performances(html_io)
    racer_winning_rate_aggregation_repository = RacerWinningRateAggregationRepository()
    racer_winning_rate_aggregation_repository.create_or_update_many(racer_performances)

    html_io.seek(0)
    if is_deadline_changed(html_io):
        raise RaceDeadlineChanged


@app.task
def crawl_all_race_information_for_date_and_stadiums(
    date: date, stadium_tel_codes: list[StadiumTelCode]
) -> None:
    for stadium_tel_code in stadium_tel_codes:
        for race_number in range(1, 13):
            try:
                crawl_race_information_page(stadium_tel_code.value, date, race_number)
                time.sleep(3)
            except Exception as e:
                # TODO: バグトラッキングシステムに通知
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Error crawling race {race_number} at {stadium_tel_code.name} on {date}: {e}"
                )


@app.task
def crawl_race_before_information_page(stadium_tel_code: int, date: date, race_number: int) -> None:
    url = create_race_before_information_page_url(
        date, StadiumTelCode(stadium_tel_code), race_number
    )
    html_io = fetch_html_as_io(url)
    start_exhibition_records = extract_start_exhibition_records(html_io)
    if not start_exhibition_records:
        try:
            crawl_race_result_page(StadiumTelCode(stadium_tel_code), date, race_number)
        except RaceCanceled:
            raise
        except Exception as e:
            raise DataNotFound from e

    start_exhibition_record_repository = StartExhibitionRecordRepository()
    start_exhibition_record_repository.create_or_update_many(start_exhibition_records)

    html_io.seek(0)
    circumference_exhibition_records = extract_circumference_exhibition_records(html_io)
    if not circumference_exhibition_records:
        raise RaceCanceled

    circumference_exhibition_record_repository = CircumferenceExhibitionRecordRepository()
    circumference_exhibition_record_repository.create_or_update_many(
        circumference_exhibition_records
    )

    html_io.seek(0)
    racer_conditions = extract_racer_conditions(html_io)
    racer_condition_repository = RacerConditionRepository()
    racer_condition_repository.create_or_update_many(racer_conditions)

    html_io.seek(0)
    boat_settings = extract_boat_settings(html_io)
    boat_setting_repository = BoatSettingRepository()
    boat_setting_repository.create_or_update_many(boat_settings, ["tilt", "is_propeller_renewed"])

    motor_maintenance_repsitory = MotorMaintenanceRepository()
    motor_maintenance_repsitory.create_or_update_many(
        [b for b in boat_settings if len(b.motor_parts_exchanges) > 0]
    )

    html_io.seek(0)
    try:
        weather_condition = extract_weather_condition(html_io)
    except ValueError as e:
        raise IncompleteDataError from e
    weather_condition_repository = WeatherConditionRepository()
    weather_condition_repository.create_or_update(weather_condition)


@app.task
def crawl_trifecta_odds_page(stadium_tel_code: int, date: date, race_number: int) -> None:
    url = create_odds_page_url(date, StadiumTelCode(stadium_tel_code), race_number)
    html_io = fetch_html_as_io(url)
    odds = extract_odds(html_io)
    odds_repository = OddsRepository()
    odds_repository.create_or_update_many(odds)


@app.task
def crawl_race_result_page(stadium_tel_code: int, date: date, race_number: int) -> None:
    url = create_race_result_page_url(date, StadiumTelCode(stadium_tel_code), race_number)
    html_io = fetch_html_as_io(url)
    payoffs = extract_race_payoffs(html_io)
    payoff_repository = PayoffRepository()
    payoff_repository.create_or_update_many(payoffs)

    html_io = fetch_html_as_io(url)
    weather_condition = extract_weather_condition_in_performance(html_io)
    weather_condition_repository = WeatherConditionRepository()
    weather_condition_repository.create_or_update(weather_condition)

    html_io = fetch_html_as_io(url)
    race_records = extract_race_records(html_io)
    race_record_repository = RaceRecordRepository()
    race_record_repository.create_or_update_many(race_records)
    winning_race_entry_repository = WinningRaceEntryRepository()
    winning_race_entry_repository.create_or_update_many(
        [r for r in race_records if r.winning_trick is not None]
    )
    disqualified_race_entry_repository = DisqualifiedRaceEntryRepository()
    disqualified_race_entry_repository.create_or_update_many(
        [r for r in race_records if r.disqualification is not None]
    )
