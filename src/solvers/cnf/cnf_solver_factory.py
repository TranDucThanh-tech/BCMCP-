from src.solvers.registry import Registry


class CnfSolverFactory(Registry):
    @classmethod
    def create(cls, strategy: str, graph, ub: int, lb: int, *,
               encoder_name: str, sat_solver_name: str):
        return cls.get(strategy)(graph, ub, lb,
                                 encoder_name=encoder_name,
                                 sat_solver_name=sat_solver_name)