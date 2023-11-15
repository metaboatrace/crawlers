from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def create_or_update(self, entity: T) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_or_update_many(self, data: list[T]) -> bool:
        raise NotImplementedError
