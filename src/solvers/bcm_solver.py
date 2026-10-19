from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SolveResult:
    span: int | None                 # None nếu UB không khả thi
    ends: dict[int, int] | None      # màu cuối của từng đỉnh
    proven_optimal: bool = False


class BCMSolver(ABC):
    def __init__(self, graph, encoder_name: str, ub: int, lb: int = 1,
                 sat_solver_name: str = "cadical153"):
        self.graph = graph
        self.encoder_name = encoder_name
        self.ub = ub
        self.lb = lb
        self.sat_solver_name = sat_solver_name
        
    @abstractmethod
    def run(self) -> SolveResult:
        """Tìm span nhỏ nhất."""