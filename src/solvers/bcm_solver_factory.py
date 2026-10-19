from src.bcm.bcm_problem import BCMProblem  # nếu cần type hint


class BCMSolverFactory:
    _registry = {}

    @classmethod
    def register(cls, name: str):
        """Decorator chỉ nhận vào tên của solver"""
        def decorator(solver_cls):
            cls._registry[name.lower()] = solver_cls
            return solver_cls
        return decorator

    @classmethod
    def create(cls, name: str, graph, encoder_name: str, ub: int, lb: int = 1, **kwargs):
        solver_cls = cls._registry.get(name.lower())
        if not solver_cls:
            raise ValueError(f"Không tìm thấy solver với tên: '{name}'")
        return solver_cls(graph, encoder_name, ub, lb, **kwargs)