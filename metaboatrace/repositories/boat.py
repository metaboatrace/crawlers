from typing import Any

from metaboatrace.models.boat import BoatPerformance, MotorPerformance

# hack: こっちのリポジトリでは boat モジュールに置いてるので統一したい
from metaboatrace.models.race import BoatSetting as BoatSettingEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.boat import (
    BoatBettingContributeRateAggregation as BoatBettingContributeRateAggregationOrm,
)
from metaboatrace.orm.models.boat import BoatSetting as BoatSettingOrm
from metaboatrace.orm.models.boat import (
    MotorBettingContributeRateAggregation as MotorBettingContributeRateAggregationOrm,
)
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


def _transform_boat_setting_entity(entity: BoatSettingEntity) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "boat_number": entity.boat_number,
        "motor_number": entity.motor_number,
        "tilt": entity.tilt,
        "propeller_renewed": entity.is_new_propeller,
    }


class BoatSettingRepository(Repository[BoatSettingEntity]):
    def create_or_update(self, entity: BoatSettingEntity) -> bool:
        return self.create_or_update_many([entity], ["tilt", "propeller_renewed"])

    def create_or_update_many(
        self, data: list[BoatSettingEntity], on_duplicate_key_update: list[str]
    ) -> bool:
        values = [_transform_boat_setting_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            BoatSettingOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_boat_performance_entity(entity: BoatPerformance) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "boat_number": entity.number,
        "aggregated_on": entity.recorded_date,
        "quinella_rate": entity.quinella_rate,
        "trio_rate": entity.trio_rate,
    }


class BoatBettingContributeRateAggregationRepository(Repository[BoatPerformance]):
    def create_or_update(self, entity: BoatPerformance) -> bool:
        return self.create_or_update_many([entity], ["quinella_rate", "trio_rate"])

    def create_or_update_many(
        self,
        data: list[BoatPerformance],
        on_duplicate_key_update: list[str] = ["quinella_rate", "trio_rate"],
    ) -> bool:
        values = [_transform_boat_performance_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            BoatBettingContributeRateAggregationOrm,
            values,
            on_duplicate_key_update,
        )


def _transform_motor_performance_entity(entity: MotorPerformance) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "motor_number": entity.number,
        "aggregated_on": entity.recorded_date,
        "quinella_rate": entity.quinella_rate,
        "trio_rate": entity.trio_rate,
    }


class MotorBettingContributeRateAggregationRepository(Repository[MotorPerformance]):
    def create_or_update(self, entity: MotorPerformance) -> bool:
        return self.create_or_update_many([entity], ["quinella_rate", "trio_rate"])

    def create_or_update_many(
        self,
        data: list[MotorPerformance],
        on_duplicate_key_update: list[str] = ["quinella_rate", "trio_rate"],
    ) -> bool:
        values = [_transform_motor_performance_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            MotorBettingContributeRateAggregationOrm,
            values,
            on_duplicate_key_update,
        )
