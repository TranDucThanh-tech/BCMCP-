import importlib
import pkgutil

from .registry import Registry                          # noqa: F401
from .bcm_solver import BCMSolver, SolveResult          # noqa: F401
from .family import SolverFamily, SolverFamilyFactory   # noqa: F401

# Mỗi thư mục con là một họ: tự nạp để các decorator @register chạy.
for _, _name, _is_pkg in pkgutil.iter_modules(__path__):
    if _is_pkg:
        try:
            importlib.import_module(f"{__name__}.{_name}")
        except ImportError as e:        # thiếu thư viện ngoài (ortools, gurobipy, ...)
            print(f"[solvers] bỏ qua họ '{_name}': {e}")