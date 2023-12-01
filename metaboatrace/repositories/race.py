from typing import Any

from metaboatrace.models.race import (
    CircumferenceExhibitionRecord as CircumferenceExhibitionRecordEntity,
)
from metaboatrace.models.race import Odds as OddsEntity
from metaboatrace.models.race import Payoff as PayoffEntity
from metaboatrace.models.race import RaceEntry as RaceEntryEntity
from metaboatrace.models.race import RaceInformation as RaceEntity
from metaboatrace.models.race import RaceRecord as RaceRecordEntity
from metaboatrace.models.race import StartExhibitionRecord as StartExhibitionRecordEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.race import (
    CircumferenceExhibitionRecord as CircumferenceExhibitionRecordOrm,
)
from metaboatrace.orm.models.race import Odds as OddsOrm
from metaboatrace.orm.models.race import Payoff as PayoffOrm
from metaboatrace.orm.models.race import Race as RaceOrm
from metaboatrace.orm.models.race import RaceEntry as RaceEntryOrm
from metaboatrace.orm.models.race import RaceRecord as RaceRecordOrm
from metaboatrace.orm.models.race import StartExhibitionRecord as StartExhibitionRecordOrm
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


def _transform_race_entity(entity: RaceEntity) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "title": entity.title,
        "course_fixed": entity.is_course_fixed,
        "use_stabilizer": entity.use_stabilizer,
        "number_of_laps": entity.number_of_laps,
        "betting_deadline_at": entity.deadline_at,
    }


class RaceRepository(Repository[RaceEntity]):
    def create_or_update(self, entity: RaceEntity) -> bool:
        return self.create_or_update_many(
            [entity],
            ["title", "course_fixed", "number_of_laps", "use_stabilizer", "betting_deadline_at"],
        )

    def create_or_update_many(
        self,
        data: list[RaceEntity],
        on_duplicate_key_update: list[str] = [
            "title",
            "course_fixed",
            "number_of_laps",
            "use_stabilizer",
            "betting_deadline_at",
        ],
    ) -> bool:
        values = [_transform_race_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RaceOrm,
            values,
            ["title", "course_fixed", "number_of_laps", "use_stabilizer", "betting_deadline_at"],
        )


def _transform_race_entry_entity(entity: RaceEntryEntity) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "racer_registration_number": entity.racer_registration_number,
    }


class RaceEntryRepository(Repository[RaceEntryEntity]):
    def create_or_update(self, entity: RaceEntryEntity) -> bool:
        return self.create_or_update_many([entity], ["racer_registration_number"])

    def create_or_update_many(
        self,
        data: list[RaceEntryEntity],
        on_duplicate_key_update: list[str] = ["racer_registration_number"],
    ) -> bool:
        values = [_transform_race_entry_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RaceEntryOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_start_exhibition_record_entity(
    entity: StartExhibitionRecordEntity,
) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "course_number": entity.start_course,
        "start_time": entity.start_time,
    }


class StartExhibitionRecordRepository(Repository[StartExhibitionRecordEntity]):
    def create_or_update(self, entity: StartExhibitionRecordEntity) -> bool:
        return self.create_or_update_many([entity], ["course_number", "start_time"])

    def create_or_update_many(
        self,
        data: list[StartExhibitionRecordEntity],
        on_duplicate_key_update: list[str] = ["course_number", "start_time"],
    ) -> bool:
        values = [_transform_start_exhibition_record_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            StartExhibitionRecordOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_circumference_exhibition_record_entity(
    entity: CircumferenceExhibitionRecordEntity,
) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "exhibition_time": entity.exhibition_time,
    }


class CircumferenceExhibitionRecordRepository(Repository[CircumferenceExhibitionRecordEntity]):
    def create_or_update(self, entity: CircumferenceExhibitionRecordEntity) -> bool:
        return self.create_or_update_many([entity], ["exhibition_time"])

    def create_or_update_many(
        self,
        data: list[CircumferenceExhibitionRecordEntity],
        on_duplicate_key_update: list[str] = ["exhibition_time"],
    ) -> bool:
        values = [_transform_circumference_exhibition_record_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            CircumferenceExhibitionRecordOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_odds_entity(
    entity: OddsEntity,
) -> dict[str, Any]:
    betting_number = int("".join(map(str, entity.betting_numbers)))

    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "betting_method": entity.betting_method.value,
        "betting_number": betting_number,
        "ratio": entity.ratio,
    }


class OddsRepository(Repository[OddsEntity]):
    def create_or_update(self, entity: OddsEntity) -> bool:
        return self.create_or_update_many([entity], ["ratio"])

    def create_or_update_many(
        self,
        data: list[OddsEntity],
        on_duplicate_key_update: list[str] = ["ratio"],
    ) -> bool:
        values = [_transform_odds_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            OddsOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_payoff_entity(
    entity: PayoffEntity,
) -> dict[str, Any]:
    betting_number = int("".join(map(str, entity.betting_numbers)))

    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "betting_method": entity.betting_method.value,
        "betting_number": betting_number,
        "amount": entity.amount,
    }


class PayoffRepository(Repository[PayoffEntity]):
    def create_or_update(self, entity: PayoffEntity) -> bool:
        return self.create_or_update_many([entity], ["amount"])

    def create_or_update_many(
        self,
        data: list[PayoffEntity],
        on_duplicate_key_update: list[str] = ["amount"],
    ) -> bool:
        values = [_transform_payoff_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            PayoffOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_race_record_entity(
    entity: RaceRecordEntity,
) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "course_number": entity.start_course,
        "start_time": entity.start_time,
        "race_time": entity.total_time,
        "arrival": entity.arrival,
    }


class RaceRecordRepository(Repository[RaceRecordEntity]):
    def create_or_update(self, entity: RaceRecordEntity) -> bool:
        return self.create_or_update_many(
            [entity], ["course_number", "start_time", "race_time", "arrival"]
        )

    def create_or_update_many(
        self,
        data: list[RaceRecordEntity],
        on_duplicate_key_update: list[str] = [
            "course_number",
            "start_time",
            "race_time",
            "arrival",
        ],
    ) -> bool:
        values = [_transform_race_record_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RaceRecordOrm,
            values,
            on_duplicate_key_update,
        )
