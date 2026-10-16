from src.data_reader.graph_reader import GraphReader
from src.encoders.cardinality.cardinality_encoder import CardinalityEncoder
from src.encoders.cardinality.sequential_counter_encoder import SequentialCounterEncoder
from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.view.cnf_view import CNFView
from src.solvers.sat_solver import SATSolver
from src.bcm.bcm_validator import BCMValidator

reader = GraphReader("data/test.txt")
graph = reader.read()

problem = BCMProblem(graph, 49)
encoder = BCMEncoderFactory.create("sequential_counter", problem)
view = CNFView(encoder.vm)
clause = encoder.encode()
model = SATSolver(clause).solve()
tester = BCMValidator(model, problem, encoder.vm)
tester.run_all_tests()