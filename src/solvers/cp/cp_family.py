from src.solvers.cp.cp_solver_factory import CpSolverFactory
from src.solvers.family import SolverFamily, SolverFamilyFactory


@SolverFamilyFactory.register("cp")
class CpFamily(SolverFamily):
    @classmethod
    def add_arguments(cls, parser):
        g = parser.add_argument_group("cp")
        g.add_argument("--time-limit", type=float, default=None)
        g.add_argument("--workers", type=int, default=8)

    @classmethod
    def create(cls, strategy, graph, ub, lb, args):
        return CpSolverFactory.create(strategy, graph, ub, lb,
                                      time_limit=args.time_limit,
                                      workers=args.workers)

    @classmethod
    def strategies(cls):
        return CpSolverFactory.names()