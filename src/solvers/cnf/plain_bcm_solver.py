from pysat.solvers import Solver

from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.solvers.cnf.cnf_solver_factory import CnfSolverFactory
from src.solvers.cnf.iterative_bcm_solver import IterativeBCMSolver


@CnfSolverFactory.register("plain")
class PlainBCMSolver(IterativeBCMSolver):
    def prepare(self):
        self.max_weight = max(v.weight for v in self.graph.get_vertices())

    def solve_with_span_at_most(self, k):
        if k < self.max_weight:
            return None                          # có đỉnh không thể kết thúc <= k
        encoder = BCMEncoderFactory.create(self.encoder_name, BCMProblem(self.graph, k))
        clauses = encoder.encode_vertex_constraint() + encoder.encode_distance_constraint()
        with Solver(name=self.sat_solver_name, bootstrap_with=clauses) as solver:
            if not solver.solve():
                return None
            return encoder.decode_ends({l for l in solver.get_model() if l > 0})