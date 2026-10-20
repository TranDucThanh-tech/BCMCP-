from .bcm_encoder import BCMEncoder                        # noqa: F401
from .bcm_encoder_factory import BCMEncoderFactory         # noqa: F401

# import để các decorator @register chạy
from . import bcm_pairwise_encoder                         # noqa: F401  -> "pairwise"
from . import bcm_order_encoder                            # noqa: F401  -> "order"
from . import bcm_sequential_counter_encoder               # noqa: F401  -> "sequential_counter"