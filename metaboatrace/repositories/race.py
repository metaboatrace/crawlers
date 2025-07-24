from datetime import date
from typing import Any

from metaboatrace.models.race import (
    CircumferenceExhibitionRecord as CircumferenceExhibitionRecordEntity,
)
from metaboatrace.models.race import Disqualification
from metaboatrace.models.race import Odds as OddsEntity
from metaboatrace.models.race import Payoff as PayoffEntity
from metaboatrace.models.race import RaceEntry as RaceEntryEntity
from metaboatrace.models.race import RaceInformation as RaceEntity
from metaboatrace.models.race import RaceRecord as RaceRecordEntity
from metaboatrace.models.race import StartExhibitionRecord as StartExhibitionRecordEntity
from metaboatrace.models.stadium import StadiumTelCode
from metaboatrace.orm.database import Session
from metaboatrace.orm.models.race import (
    CircumferenceExhibitionRecord as CircumferenceExhibitionRecordOrm,
)
from metaboatrace.orm.models.race import DisqualifiedRaceEntry as DisqualifiedRaceEntryOrm
from metaboatrace.orm.models.race import Odds as OddsOrm
from metaboatrace.orm.models.race import Payoff as PayoffOrm
from metaboatrace.orm.models.race import Race as RaceOrm
from metaboatrace.orm.models.race import RaceEntry as RaceEntryOrm
from metaboatrace.orm.models.race import RaceRecord as RaceRecordOrm
from metaboatrace.orm.models.race import StartExhibitionRecord as StartExhibitionRecordOrm
from metaboatrace.orm.models.race import WinningRaceEntry as WinningRaceEntryOrm
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


def _transform_race_entity(entity: RaceEntity) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "title": entity.title,
        "is_course_fixed": entity.is_course_fixed,
        "is_stabilizer_used": entity.use_stabilizer,
        "number_of_laps": entity.number_of_laps,
        "betting_deadline_at": entity.deadline_at,
    }


def _race_orm_to_entity(race_orm: RaceOrm) -> RaceEntity:
    return RaceEntity(
        race_holding_date=race_orm.date,
        stadium_tel_code=StadiumTelCode(race_orm.stadium_tel_code),
        race_number=race_orm.race_number,
        title=race_orm.title,
        number_of_laps=race_orm.number_of_laps,
        deadline_at=race_orm.betting_deadline_at,
        is_course_fixed=race_orm.is_course_fixed,
        use_stabilizer=race_orm.is_stabilizer_used,
    )


class RaceRepository(Repository[RaceEntity]):
    def find_by_key(self, stadium_tel_code: int, date: date, race_number: int) -> RaceEntity | None:
        session = Session()
        try:
            race_orm = (
                session.query(RaceOrm)
                .filter_by(stadium_tel_code=stadium_tel_code, date=date, race_number=race_number)
                .first()
            )
            if race_orm is not None:
                return _race_orm_to_entity(race_orm)
            return None
        finally:
            session.close()

    def find_all_by_date(self, date: date) -> list[RaceEntity]:
        session = Session()
        try:
            race_orms = session.query(RaceOrm).filter_by(date=date).all()
            return [_race_orm_to_entity(race_orm) for race_orm in race_orms]
        finally:
            session.close()

    def create_or_update(self, entity: RaceEntity) -> bool:
        return self.create_or_update_many(
            [entity],
            [
                "title",
                "is_course_fixed",
                "number_of_laps",
                "is_stabilizer_used",
                "betting_deadline_at",
            ],
        )

    def create_or_update_many(
        self,
        data: list[RaceEntity],
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = [
                "title",
                "is_course_fixed",
                "number_of_laps",
                "is_stabilizer_used",
                "betting_deadline_at",
            ]
        values = [_transform_race_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RaceOrm,
            values,
            on_duplicate_key_update,
        )

    def cancel(self, stadium_tel_code: int, date: date, race_number: int) -> bool:
        session = Session()

        try:
            race_orm = (
                session.query(RaceOrm)
                .filter_by(stadium_tel_code=stadium_tel_code, date=date, race_number=race_number)
                .first()
            )

            if not race_orm:
                race_orm = RaceOrm(
                    stadium_tel_code=stadium_tel_code,
                    date=date,
                    race_number=race_number,
                    is_canceled=True,
                )
                session.add(race_orm)
            else:
                race_orm.is_canceled = True  # type: ignore

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()


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
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = ["racer_registration_number"]
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
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = ["course_number", "start_time"]
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
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = ["exhibition_time"]
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
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = ["ratio"]
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
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = ["amount"]
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
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = [
                "course_number",
                "start_time",
                "race_time",
                "arrival",
            ]
        values = [
            _transform_race_record_entity(entity)
            for entity in data
            if (entity.disqualification != Disqualification.ABSENT)
            and not (
                entity.disqualification == Disqualification.LATENESS and entity.start_course is None
            )
        ]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RaceRecordOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_race_record_entity_to_winning_race_entry(
    entity: RaceRecordEntity,
) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "winning_trick": entity.winning_trick.value,
    }


class WinningRaceEntryRepository(Repository[RaceRecordEntity]):
    def create_or_update(self, entity: RaceRecordEntity) -> bool:
        return self.create_or_update_many([entity], ["winning_trick"])

    def create_or_update_many(
        self,
        data: list[RaceRecordEntity],
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = [
                "winning_trick",
            ]
        values = [_transform_race_record_entity_to_winning_race_entry(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            WinningRaceEntryOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_race_record_entity_to_disqualified_race_entry(
    entity: RaceRecordEntity,
) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "disqualification": entity.disqualification.value,
    }


class DisqualifiedRaceEntryRepository(Repository[RaceRecordEntity]):
    def create_or_update(self, entity: RaceRecordEntity) -> bool:
        return self.create_or_update_many([entity], ["disqualification"])

    def create_or_update_many(
        self,
        data: list[RaceRecordEntity],
        on_duplicate_key_update: list[str] | None = None,
    ) -> bool:
        if on_duplicate_key_update is None:
            on_duplicate_key_update = [
                "disqualification",
            ]
        values = [
            _transform_race_record_entity_to_disqualified_race_entry(entity) for entity in data
        ]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            DisqualifiedRaceEntryOrm,
            values,
            on_duplicate_key_update,
        )
