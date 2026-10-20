from . import plain_bcm_solver          # noqa: F401
from . import incremental_bcm_solver    # noqa: F401

try:
    from . import maxsat_bcm_solver     # noqa: F401  (cần RC2)
except ImportError as e:
    print(f"[cnf] bỏ qua 'maxsat': {e}")

from . import cnf_family                # noqa: F401