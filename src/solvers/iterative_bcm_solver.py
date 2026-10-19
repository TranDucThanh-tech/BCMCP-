from pysat.solvers import Cadical153
from src.solvers.bcm_solver import BCMSolver, SolveResult
from abc import abstractmethod


class IterativeBCMSolver(BCMSolver):
    sat_solver_cls = Cadical153          # đổi solver bằng cách override thuộc tính này

    @abstractmethod
    def solve_with_span_at_most(self, k: int) -> dict[int, int] | None:
        """Màu cuối của từng đỉnh nếu có nghiệm span <= k, ngược lại None."""

    def prepare(self) -> None: ...       # hook
    def close(self) -> None: ...         # hook

    def run(self) -> SolveResult:
        self.prepare()
        try:
            best_span, best_ends, k = None, None, self.ub
            while k >= self.lb:
                ends = self.solve_with_span_at_most(k)
                if ends is None:
                    return SolveResult(best_span, best_ends, proven_optimal=best_span is not None)
                best_span, best_ends = max(ends.values()), ends
                k = best_span - 1
            return SolveResult(best_span, best_ends, proven_optimal=True)   # k < LB
        finally:
            self.close()