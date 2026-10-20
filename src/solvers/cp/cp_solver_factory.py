from src.solvers.registry import Registry


class CpSolverFactory(Registry):
    @classmethod
    def create(cls, strategy: str, graph, ub: int, lb: int, *,
               time_limit=None, workers: int = 8):
        return cls.get(strategy)(graph, ub, lb,
                                 time_limit=time_limit, workers=workers)