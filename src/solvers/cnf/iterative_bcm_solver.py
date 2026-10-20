from abc import abstractmethod

from src.solvers.bcm_solver import SolveResult
from src.solvers.cnf.cnf_bcm_solver import CnfBCMSolver


class IterativeBCMSolver(CnfBCMSolver):
    """Template method: vòng lặp giảm K viết một lần."""

    @abstractmethod
    def solve_with_span_at_most(self, k: int) -> dict[int, int] | None:
        """Màu cuối của từng đỉnh nếu có nghiệm span <= k, ngược lại None."""

    def prepare(self) -> None: ...
    def close(self) -> None: ...

    def run(self) -> SolveResult:
        try:
            self.prepare()
        except ValueError:                       # UB < weight của một đỉnh
            self.close()
            return SolveResult(None, None)

        try:
            best_span, best_ends, k = None, None, self.ub
            while k >= self.lb:
                ends = self.solve_with_span_at_most(k)
                if ends is None:
                    return SolveResult(best_span, best_ends,
                                       proven_optimal=best_span is not None)
                best_span, best_ends = max(ends.values()), ends
                k = best_span - 1
            return SolveResult(best_span, best_ends, proven_optimal=True)
        finally:
            self.close()