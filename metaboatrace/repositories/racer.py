from metaboatrace.models.racer import Racer as DomainRacer

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.racer import Racer as OrmRacer

from .base import Repository


class RacerRepository(Repository[DomainRacer]):
    def create_or_update(self, entity: DomainRacer) -> bool:
        session = Session()

        try:
            orm_racer = (
                session.query(OrmRacer)
                .filter_by(registration_number=entity.registration_number)
                .first()
            )
            if orm_racer is None:
                orm_racer = OrmRacer()
                session.add(orm_racer)

            orm_racer.registration_number = entity.registration_number
            orm_racer.last_name = entity.last_name
            orm_racer.first_name = entity.first_name
            orm_racer.gender = entity.gender.value if entity.gender else None
            orm_racer.term = entity.term
            orm_racer.birth_date = entity.birth_date
            orm_racer.branch_id = entity.branch.value if entity.branch else None
            orm_racer.birth_prefecture_id = (
                entity.born_prefecture.value if entity.born_prefecture else None
            )
            orm_racer.height = entity.height
            orm_racer.status = "active"

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        return True
