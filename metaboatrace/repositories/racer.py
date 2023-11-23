from enum import Enum

from metaboatrace.models.racer import Racer as RacerEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.racer import Racer as RacerOrm
from metaboatrace.orm.strategies.upsert import create_upsert_strategy

from .base import Repository


class RacerStatus(Enum):
    active = 1
    retired = 2


class RacerRepository(Repository[RacerEntity]):
    def create_or_update(self, entity: RacerEntity) -> bool:
        session = Session()

        try:
            orm_racer = (
                session.query(RacerOrm)
                .filter_by(registration_number=entity.registration_number)
                .first()
            )
            if orm_racer is None:
                orm_racer = RacerOrm()
                session.add(orm_racer)

            orm_racer.registration_number = entity.registration_number
            orm_racer.last_name = entity.last_name
            orm_racer.first_name = entity.first_name
            if orm_racer.gender is None:
                orm_racer.gender = entity.gender.value if entity.gender else None
            orm_racer.term = entity.term
            orm_racer.birth_date = entity.birth_date
            orm_racer.branch_id = entity.branch.value if entity.branch else None
            orm_racer.birth_prefecture_id = (
                entity.born_prefecture.value if entity.born_prefecture else None
            )
            orm_racer.height = entity.height
            orm_racer.status = RacerStatus.active.value

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        return True

    def create_or_update_many(self, data: list[RacerEntity]) -> bool:
        values = [
            {
                "registration_number": racer.registration_number,
                "last_name": racer.last_name,
                "first_name": racer.first_name,
                "gender": racer.gender.value if racer.gender else None,
                "term": racer.term,
                "birth_date": racer.birth_date,
                "branch_id": racer.branch.value if racer.branch else None,
                "birth_prefecture_id": racer.born_prefecture.value
                if racer.born_prefecture
                else None,
                "height": racer.height,
            }
            for racer in data
        ]

        upsert_strategy = create_upsert_strategy()
        session = Session()

        return upsert_strategy(session, RacerOrm, values, ["gender"])
