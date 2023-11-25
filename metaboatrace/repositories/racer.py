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
