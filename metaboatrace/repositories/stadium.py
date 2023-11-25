from metaboatrace.models.stadium import Event as EventEntity
from metaboatrace.models.stadium import MotorRenewal as MotorRenewalEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.stadium import Event as EventOrm
from metaboatrace.orm.models.stadium import MotorRenewal as MotorRenewalOrm
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


class EventRepository(Repository[EventEntity]):
    def create_or_update(self, entity: EventEntity) -> bool:
        raise NotImplementedError

    def create_or_update_many(self, data: list[EventEntity]) -> bool:
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
            ["grade", "kind"],
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

    def create_or_update_many(self, data: list[EventEntity]) -> bool:
        raise NotImplementedError
