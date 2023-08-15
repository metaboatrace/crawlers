from injector import Binder, Module, singleton

from ..repositories import RacerRepository


class RepositoryModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(RacerRepository, to=RacerRepository, scope=singleton)
