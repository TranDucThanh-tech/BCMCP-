from src.solvers.iterative_bcm_solver import IterativeBCMSolver
from src.solvers.bcm_solver_factory import BCMSolverFactory
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.bcm.bcm_problem import BCMProblem
from pysat.solvers import Solver

@BCMSolverFactory.register("plain")
class PlainBCMSolver(IterativeBCMSolver):
    def solve_with_span_at_most(self, k):
        encoder = BCMEncoderFactory.create(self.encoder_name, BCMProblem(self.graph, k))
        try:
            clauses = encoder.encode_vertex_constraint() + encoder.encode_distance_constraint()
        except ValueError:
            return None                  # k < weight => UNSAT
        with Solver(name=self.sat_solver_name, bootstrap_with=clauses) as solver:
            if not solver.solve():
                return None
            return encoder.decode_ends({l for l in solver.get_model() if l > 0})