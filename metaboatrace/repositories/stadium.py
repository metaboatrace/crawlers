from metaboatrace.models.stadium import Event as EventEntity

from metaboatrace.orm.database import Session
from metaboatrace.orm.models.stadium import Event as EventOrm
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
