from src.solvers.cnf.cnf_solver_factory import CnfSolverFactory
from src.solvers.family import SolverFamily, SolverFamilyFactory


@SolverFamilyFactory.register("cnf")
class CnfFamily(SolverFamily):
    @classmethod
    def add_arguments(cls, parser):
        g = parser.add_argument_group("cnf")
        g.add_argument("--encoder", default="sequential_counter")
        g.add_argument("--sat", default="cadical153", help="engine SAT của PySAT")

    @classmethod
    def create(cls, strategy, graph, ub, lb, args):
        return CnfSolverFactory.create(strategy, graph, ub, lb,
                                       encoder_name=args.encoder,
                                       sat_solver_name=args.sat)

    @classmethod
    def strategies(cls):
        return CnfSolverFactory.names()