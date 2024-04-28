from enum import Enum
from typing import Any

from metaboatrace.models.racer import Racer as RacerEntity
from metaboatrace.models.racer import RacerCondition as RacerConditionEntity
from metaboatrace.models.racer import RacerPerformance as RacerPerformanceEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.racer import Racer as RacerOrm
from metaboatrace.orm.models.racer import RacerCondition as RacerConditionOrm
from metaboatrace.orm.models.racer import (
    RacerWinningRateAggregation as RacerWinningRateAggregationOrm,
)
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


class RacerStatus(Enum):
    active = 1
    retired = 2


class RacerRepository(Repository[RacerEntity]):
    def create_or_update(self, entity: RacerEntity) -> bool:
        session = Session()

        try:
            racer_orm = (
                session.query(RacerOrm)
                .filter_by(registration_number=entity.registration_number)
                .first()
            )
            if racer_orm is None:
                racer_orm = RacerOrm()
                session.add(racer_orm)

            racer_orm.registration_number = entity.registration_number
            racer_orm.last_name = entity.last_name
            racer_orm.first_name = entity.first_name
            if racer_orm.gender is None:
                racer_orm.gender = entity.gender.value if entity.gender else None
            racer_orm.term = entity.term
            racer_orm.birth_date = entity.birth_date
            racer_orm.branch_id = entity.branch.value if entity.branch else None
            racer_orm.birth_prefecture_id = (
                entity.born_prefecture.value if entity.born_prefecture else None
            )
            racer_orm.height = entity.height
            racer_orm.status = RacerStatus.active.value

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        return True

    def create_or_update_many(
        self, data: list[RacerEntity], on_duplicate_key_update: list[str] = ["gender"]
    ) -> bool:
        values = [
            {
                "registration_number": racer.registration_number,
                "last_name": racer.last_name,
                "first_name": racer.first_name,
                "gender": racer.gender.value if racer.gender else None,
                "term": racer.term,
                "birth_date": racer.birth_date,
                "branch_id": racer.branch.value if racer.branch else None,
                "birth_prefecture_id": (
                    racer.born_prefecture.value if racer.born_prefecture else None
                ),
                "height": racer.height,
            }
            for racer in data
        ]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(session, RacerOrm, values, on_duplicate_key_update)

    def make_retired(self, racer_registration_number: int) -> bool:
        session = Session()

        try:
            racer_orm = (
                session.query(RacerOrm)
                .filter_by(registration_number=racer_registration_number)
                .first()
            )
            if racer_orm is None:
                racer_orm = RacerOrm(registration_number=racer_registration_number)
                session.add(racer_orm)

            racer_orm.status = RacerStatus.retired.value

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        return True


def _transform_racer_condition_entity(
    entity: RacerConditionEntity,
) -> dict[str, Any]:
    return {
        "racer_registration_number": entity.racer_registration_number,
        "date": entity.recorded_on,
        "weight": entity.weight,
        "adjust": entity.adjust,
    }


class RacerConditionRepository(Repository[RacerConditionEntity]):
    def create_or_update(self, entity: RacerConditionEntity) -> bool:
        return self.create_or_update_many([entity], ["weight", "adjust"])

    def create_or_update_many(
        self,
        data: list[RacerConditionEntity],
        on_duplicate_key_update: list[str] = ["weight", "adjust"],
    ) -> bool:
        values = [_transform_racer_condition_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RacerConditionOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_racer_performance_entity(
    entity: RacerPerformanceEntity,
) -> dict[str, Any]:
    return {
        "racer_registration_number": entity.racer_registration_number,
        "aggregated_on": entity.aggregated_on,
        "rate_in_all_stadium": entity.rate_in_all_stadium,
        "rate_in_event_going_stadium": entity.rate_in_event_going_stadium,
    }


class RacerWinningRateAggregationRepository(Repository[RacerPerformanceEntity]):
    def create_or_update(self, entity: RacerPerformanceEntity) -> bool:
        return self.create_or_update_many(
            [entity], ["rate_in_all_stadium", "rate_in_event_going_stadium"]
        )

    def create_or_update_many(
        self,
        data: list[RacerPerformanceEntity],
        on_duplicate_key_update: list[str] = ["rate_in_all_stadium", "rate_in_event_going_stadium"],
    ) -> bool:
        values = [_transform_racer_performance_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            RacerWinningRateAggregationOrm,
            values,
            on_duplicate_key_update,
        )
