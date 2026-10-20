from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SolveResult:
    span: int | None                 # None nếu không có nghiệm
    ends: dict[int, int] | None      # màu cuối của từng đỉnh
    proven_optimal: bool = False


class BCMSolver(ABC):
    """Hợp đồng duy nhất của mọi solver: nhận đồ thị + cận, trả SolveResult."""

    def __init__(self, graph, ub: int, lb: int = 1):
        self.graph = graph
        self.ub = ub
        self.lb = lb

    @abstractmethod
    def run(self) -> SolveResult: ...