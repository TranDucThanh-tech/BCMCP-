from pysat.solvers import Solver

class SATSolver:

    def __init__(self, cnf: list[list[int]]):
        self.cnf = cnf

    def solve(self) -> list[int] | None:
        with Solver(name="g3", bootstrap_with=self.cnf) as solver:
            if solver.solve():
                return solver.get_model()

            return None

    def solve_all(self) -> list[list[int]]:
        """Tìm và trả về tất cả các nghiệm (models) thỏa mãn công thức CNF."""
        models = []
        # Sử dụng cùng loại solver (g3) như phương thức solve
        with Solver(name="g3", bootstrap_with=self.cnf) as solver:
            while solver.solve():
                model = solver.get_model()
                models.append(model)
                
                # Thêm mệnh đề chặn (blocking clause) để ép bộ giải 
                # không lặp lại nghiệm hiện tại ở các vòng lặp tiếp theo.
                # Phủ định tất cả các literal trong model hiện tại: [-l for l in model]
                solver.add_clause([-l for l in model])
                
        return models