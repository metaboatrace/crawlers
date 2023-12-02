from datetime import date
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
from metaboatrace.orm.models.boat import MotorMaintenance as MotorMaintenanceOrm
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


class MotorNumberNotFoundError(Exception):
    def __init__(self, message: str = "Motor number not found for given race entry") -> None:
        self.message = message
        super().__init__(self.message)


def _transform_boat_setting_entity(entity: BoatSettingEntity) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "pit_number": entity.pit_number,
        "boat_number": entity.boat_number,
        "motor_number": entity.motor_number,
        "tilt": entity.tilt,
        "is_propeller_renewed": entity.is_new_propeller,
    }


class BoatSettingRepository(Repository[BoatSettingEntity]):
    def create_or_update(self, entity: BoatSettingEntity) -> bool:
        return self.create_or_update_many([entity], ["tilt", "is_propeller_renewed"])

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

    def get_motor_number(
        self, stadium_tel_code: int, date: date, race_number: int, pit_number: int
    ) -> int:
        with Session() as session:
            boat_setting = (
                session.query(BoatSettingOrm)
                .filter(
                    BoatSettingOrm.stadium_tel_code == stadium_tel_code,
                    BoatSettingOrm.date == date,
                    BoatSettingOrm.race_number == race_number,
                    BoatSettingOrm.pit_number == pit_number,
                )
                .first()
            )

            if not boat_setting or boat_setting.motor_number is None:
                raise MotorNumberNotFoundError()

            return boat_setting.motor_number


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


class MotorMaintenanceRepository(Repository[BoatSettingEntity]):
    def create_or_update(self, entity: BoatSettingEntity) -> bool:
        raise NotImplementedError

    def create_or_update_many(
        self,
        data: list[BoatSettingEntity],
        on_duplicate_key_update: list[str] = ["quantity"],
    ) -> bool:
        boat_setting_repository = BoatSettingRepository()
        values = self._transform_entities_to_values(data, boat_setting_repository)

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            MotorMaintenanceOrm,
            values,
            on_duplicate_key_update,
        )

    def _transform_entities_to_values(
        self, data: list[BoatSettingEntity], boat_setting_repository: BoatSettingRepository
    ) -> list[dict[str, Any]]:
        transformed_values = []
        for entity in data:
            if not entity.motor_parts_exchanges:
                continue

            for motor_part, quantity in entity.motor_parts_exchanges:
                motor_number = boat_setting_repository.get_motor_number(
                    entity.stadium_tel_code.value,
                    entity.race_holding_date,
                    entity.race_number,
                    entity.pit_number,
                )

                transformed_values.append(
                    {
                        "stadium_tel_code": entity.stadium_tel_code.value,
                        "date": entity.race_holding_date,
                        "race_number": entity.race_number,
                        "motor_number": motor_number,
                        "exchanged_parts": motor_part.value,
                        "quantity": quantity,
                    }
                )

        return transformed_values
