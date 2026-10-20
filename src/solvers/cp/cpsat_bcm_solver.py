from ortools.sat.python import cp_model

from src.solvers.bcm_solver import BCMSolver, SolveResult
from src.solvers.cp.cp_solver_factory import CpSolverFactory


@CpSolverFactory.register("cpsat")
class CpSatBCMSolver(BCMSolver):
    """end[v] in [b(v), ub]. Mỗi cạnh chọn thứ tự bằng biến bool d:
       d     : u dưới v  =>  end[v] - b(v) >= end[u] + w
       not d : v dưới u  =>  end[u] - b(u) >= end[v] + w"""

    def __init__(self, graph, ub, lb=1, *, time_limit=None, workers=8):
        super().__init__(graph, ub, lb)
        self.time_limit = time_limit
        self.workers = workers

    def _build_model(self):
        vertices = self.graph.get_vertices()
        if any(v.weight > self.ub for v in vertices):
            return None, None

        model = cp_model.CpModel()
        end = {v.id: model.NewIntVar(v.weight, self.ub, f"e_{v.id}") for v in vertices}
        span = model.NewIntVar(self.lb, self.ub, "span")
        for v in vertices:
            model.Add(end[v.id] <= span)

        for e in self.graph.get_edges():
            u, v, w = e.u, e.v, e.weight
            d = model.NewBoolVar(f"d_{u.id}_{v.id}")
            model.Add(end[v.id] - v.weight >= end[u.id] + w).OnlyEnforceIf(d)
            model.Add(end[u.id] - u.weight >= end[v.id] + w).OnlyEnforceIf(d.Not())

        model.Minimize(span)
        return model, end

    def run(self) -> SolveResult:
        model, end = self._build_model()
        if model is None:
            return SolveResult(None, None)

        solver = cp_model.CpSolver()
        solver.parameters.num_workers = self.workers
        if self.time_limit is not None:
            solver.parameters.max_time_in_seconds = self.time_limit

        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return SolveResult(None, None)

        ends = {vid: solver.Value(var) for vid, var in end.items()}
        return SolveResult(max(ends.values()), ends,
                           proven_optimal=(status == cp_model.OPTIMAL))