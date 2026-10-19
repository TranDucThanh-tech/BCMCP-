import time

from src.data_reader.graph_reader import GraphReader
from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.view.cnf_view import CNFView
from src.solvers.sat_solver import SATSolver
from src.bcm.bcm_validator import BCMValidator
from src.encoders.bcm_problem.bcm_pairwise_encoder import BCMPairwiseEncoder  
from src.encoders.bcm_problem.bcm_order_encoder import BCMOrderEncoder       
from src.encoders.bcm_problem.bcm_sequential_counter_encoder import BCMSequentialCounterEncoder       


def timed(func, *args, **kwargs):
    """Chạy func, trả về (kết quả, thời gian CPU tính bằng giây)."""
    start = time.process_time()
    result = func(*args, **kwargs)
    return result, time.process_time() - start


reader = GraphReader("data/test.txt")
graph = reader.read()

problem = BCMProblem(graph, 49)
encoder = BCMEncoderFactory.create("pairwise", problem)
view = CNFView(encoder.vm)

# --- Encode ---
clauses, encode_time = timed(encoder.encode)

# --- Solve ---
model, solve_time = timed(SATSolver(clauses).solve)

# --- Validate ---
tester = BCMValidator(model, problem, encoder.vm)
passed, validate_time = timed(tester.run_all_tests)

# --- Thống kê ---
print("\n========================================")
print("              TIMING REPORT             ")
print("========================================")
print(f"Variables : {len(encoder.vm.obj2id) if hasattr(encoder.vm, 'obj2id') else 'n/a'}")
print(f"Clauses   : {len(clauses)}")
print(f"Encode (CPU)   : {encode_time:.4f} s")
print(f"Solve  (CPU)   : {solve_time:.4f} s")
print(f"Validate (CPU) : {validate_time:.4f} s")
print(f"Total  (CPU)   : {encode_time + solve_time + validate_time:.4f} s")
print(f"Result    : {'SAT & valid' if passed else 'UNSAT or invalid'}")
print("========================================")