from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def create_or_update(self, entity: T) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_or_update_many(self, data: list[T], on_duplicate_key_update: list[str]) -> bool:
        raise NotImplementedError
