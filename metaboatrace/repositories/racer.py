from metaboatrace.models.racer import Racer

from .base import Repository


class RacerRepository(Repository[Racer]):
    def create_or_update(self, entity: Racer) -> bool:
        raise NotImplementedError
