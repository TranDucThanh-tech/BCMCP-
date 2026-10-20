from abc import ABC, abstractmethod

from src.solvers.registry import Registry


class SolverFamily(ABC):
    """Một họ solver: tự khai báo tham số dòng lệnh, tự tạo solver từ args."""

    @classmethod
    def add_arguments(cls, parser) -> None:
        """Họ tự thêm tham số của mình. Mặc định không có."""

    @classmethod
    @abstractmethod
    def create(cls, strategy: str, graph, ub: int, lb: int, args): ...

    @classmethod
    @abstractmethod
    def strategies(cls) -> list[str]: ...


class SolverFamilyFactory(Registry):
    @classmethod
    def create(cls, family: str, strategy: str, graph, ub: int, lb: int, args):
        return cls.get(family).create(strategy, graph, ub, lb, args)