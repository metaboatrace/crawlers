from typing import Any

# todo: 名前空間の統一性の観点から stadium から import したい
from metaboatrace.models.race import WeatherCondition as WeatherConditionEntity
from metaboatrace.models.stadium import Event as EventEntity
from metaboatrace.models.stadium import MotorRenewal as MotorRenewalEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.stadium import Event as EventOrm
from metaboatrace.orm.models.stadium import MotorRenewal as MotorRenewalOrm
from metaboatrace.orm.models.stadium import WeatherCondition as WeatherConditionOrm
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


class EventRepository(Repository[EventEntity]):
    def create_or_update(self, entity: EventEntity) -> bool:
        raise NotImplementedError

    def create_or_update_many(
        self, data: list[EventEntity], on_duplicate_key_update: list[str] = ["grade", "kind"]
    ) -> bool:
        values = [
            {
                "stadium_tel_code": e.stadium_tel_code.value,
                "starts_on": e.starts_on,
                "title": e.title,
                "grade": e.grade.value,
                "kind": e.kind.value,
            }
            for e in data
        ]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            EventOrm,
            values,
            on_duplicate_key_update,
        )


class MotorRenewalRepository(Repository[MotorRenewalOrm]):
    def create_or_update(self, entity: MotorRenewalEntity) -> bool:
        session = Session()
        try:
            existing_record = (
                session.query(MotorRenewalOrm)
                .filter_by(stadium_tel_code=entity.stadium_tel_code.value, date=entity.date)
                .one_or_none()
            )

            if existing_record is None:
                new_record = MotorRenewalOrm(
                    stadium_tel_code=entity.stadium_tel_code.value, date=entity.date
                )
                session.add(new_record)
            else:
                pass

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    def create_or_update_many(
        self, data: list[EventEntity], on_duplicate_key_update: list[str]
    ) -> bool:
        raise NotImplementedError


def _transform_weather_condition_entity(
    entity: WeatherConditionEntity,
) -> dict[str, Any]:
    return {
        "stadium_tel_code": entity.stadium_tel_code.value,
        "date": entity.race_holding_date,
        "race_number": entity.race_number,
        "is_in_performance": entity.in_performance,
        "weather": entity.weather.value,
        "wavelength": entity.wavelength,
        "wind_angle": entity.wind_angle,
        "wind_velocity": entity.wind_velocity,
        "air_temperature": entity.air_temperature,
        "water_temperature": entity.water_temperature,
    }


class WeatherConditionRepository(Repository[WeatherConditionEntity]):
    def create_or_update(self, entity: WeatherConditionEntity) -> bool:
        return self.create_or_update_many(
            [entity],
            [
                "weather",
                "wind_velocity",
                "wind_angle",
                "wavelength",
                "air_temperature",
                "water_temperature",
            ],
        )

    def create_or_update_many(
        self,
        data: list[WeatherConditionEntity],
        on_duplicate_key_update: list[str] = [
            "weather",
            "wind_velocity",
            "wind_angle",
            "wavelength",
            "air_temperature",
            "water_temperature",
        ],
    ) -> bool:
        values = [_transform_weather_condition_entity(entity) for entity in data]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(
            session,
            WeatherConditionOrm,
            values,
            on_duplicate_key_update,
        )
