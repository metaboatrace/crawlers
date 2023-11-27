from typing import Any

from metaboatrace.models.race import RaceEntry as RaceEntryEntity
from metaboatrace.models.race import RaceInformation as RaceEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.race import Race as RaceOrm
from metaboatrace.orm.models.race import RaceEntry as RaceEntryOrm
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
        return self.create_or_update_many([entity])

    def create_or_update_many(self, data: list[RaceEntity]) -> bool:
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
        return self.create_or_update_many([entity])

    def create_or_update_many(self, data: list[RaceEntryEntity]) -> bool:
        values = [_transform_race_entry_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RaceEntryOrm,
            values,
            ["racer_registration_number"],
        )
