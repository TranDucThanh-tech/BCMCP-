from src.solvers.bcm_solver import BCMSolver


class CnfBCMSolver(BCMSolver):
    """Nhóm solver dùng encoder CNF."""

    def __init__(self, graph, ub: int, lb: int = 1, *,
                 encoder_name: str, sat_solver_name: str = "cadical153"):
        super().__init__(graph, ub, lb)
        self.encoder_name = encoder_name
        self.sat_solver_name = sat_solver_name