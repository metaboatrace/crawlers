from datetime import date

from metaboatrace.models.race import BoatSetting
from metaboatrace.models.stadium import StadiumTelCode
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

from metaboatrace.crawlers.utils import fetch_html_as_io
from metaboatrace.repositories import (
    BoatBettingContributeRateAggregationRepository,
    BoatSettingRepository,
    CircumferenceExhibitionRecordRepository,
    DisqualifiedRaceEntryRepository,
    MotorBettingContributeRateAggregationRepository,
    OddsRepository,
    PayoffRepository,
    RaceEntryRepository,
    RacerConditionRepository,
    RaceRecordRepository,
    RaceRepository,
    StartExhibitionRecordRepository,
    WeatherConditionRepository,
    WinningRaceEntryRepository,
)


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
    # hack: ここでやらない
    boat_settings = [
        BoatSetting(
            race_holding_date=race_entry.race_holding_date,
            stadium_tel_code=race_entry.stadium_tel_code,
            race_number=race_entry.race_number,
            pit_number=race_entry.pit_number,
            boat_number=race_entry.boat_number,
            motor_number=race_entry.motor_number,
            motor_parts_exchanges=[],
        )
        for race_entry in race_entries
    ]
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


def crawl_race_before_information_page(stadium_tel_code: int, date: date, race_number: int) -> None:
    url = create_race_before_information_page_url(
        date, StadiumTelCode(stadium_tel_code), race_number
    )
    html_io = fetch_html_as_io(url)
    start_exhibition_records = extract_start_exhibition_records(html_io)
    start_exhibition_record_repository = StartExhibitionRecordRepository()
    start_exhibition_record_repository.create_or_update_many(start_exhibition_records)

    html_io.seek(0)
    circumference_exhibition_records = extract_circumference_exhibition_records(html_io)
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

    html_io.seek(0)
    weather_condition = extract_weather_condition(html_io)
    weather_condition_repository = WeatherConditionRepository()
    weather_condition_repository.create_or_update(weather_condition)


def crawl_trifecta_odds_page(stadium_tel_code: int, date: date, race_number: int) -> None:
    url = create_odds_page_url(date, StadiumTelCode(stadium_tel_code), race_number)
    html_io = fetch_html_as_io(url)
    odds = extract_odds(html_io)
    odds_repository = OddsRepository()
    odds_repository.create_or_update_many(odds)


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
