
from src import variables
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory


@BCMEncoderFactory.register("order")
class BCMOrderEncoder(BCMEncoder):
    pass