from abc import ABC, abstractmethod
from typing import Hashable

from src.variables.variable_manager import VariableManager


class CardinalityEncoder(ABC):

    def __init__(self, vm: VariableManager):
        self.vm = vm

    def get_var(self, key: Hashable) -> int:
        return self.vm.get_var(key)

    def encode_given(self, key: Hashable) -> list[list[int]]:
        return [[self.get_var(key)]]

    @abstractmethod
    def encode_alo(
            self,
            keys: list[Hashable]
        ) -> list[list[int]]:
            variables = [self.get_var(key) for key in keys]
    
            return [variables] if variables else [[]]

    @abstractmethod
    def encode_amo(
        self,
        keys: list[Hashable]
    ) -> list[list[int]]:
        pass

    def encode_exactly_one(
        self,
        keys: list[Hashable]
    ) -> list[list[int]]:
        return (
            self.encode_alo(keys)
            + self.encode_amo(keys)
        )