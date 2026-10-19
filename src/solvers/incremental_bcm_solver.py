from src.solvers.iterative_bcm_solver import IterativeBCMSolver
from src.solvers.bcm_solver_factory import BCMSolverFactory
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.bcm.bcm_problem import BCMProblem
from pysat.solvers import Solver


@BCMSolverFactory.register("incremental")
class IncrementalBCMSolver(IterativeBCMSolver):
    def prepare(self):
        self.encoder = BCMEncoderFactory.create(
            self.encoder_name, BCMProblem(self.graph, self.ub))
        clauses = self.encoder.encode_vertex_constraint() + self.encoder.encode_distance_constraint() + self.encoder.encode_bound_constraint()
        self.solver = Solver(name=self.sat_solver_name, bootstrap_with=clauses)

    def solve_with_span_at_most(self, k):
        assumptions = self.encoder.span_assumptions(k)
        if assumptions is None or not self.solver.solve(assumptions=assumptions):
            return None
        return self.encoder.decode_ends({l for l in self.solver.get_model() if l > 0})

    def close(self):
        self.solver.delete()