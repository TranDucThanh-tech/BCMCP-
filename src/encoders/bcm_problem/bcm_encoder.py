from abc import abstractmethod

from src.variables.variable_manager import VariableManager
from src.bcm.bcm_problem import BCMProblem

class BCMEncoder:
    def __init__(self, bcm_problem: BCMProblem):
        self.bcm_problem = bcm_problem
        self.vm = VariableManager()
        self.cardinality_encoder = None  # This will be set in subclasses

    def encode(self) -> list[list[int]]:
        clauses = []
        clauses.extend(self.encode_vertex_constraint())
        clauses.extend(self.encode_distance_constraint())
        return clauses

    def get_var(self, key):
        return self.vm.get_var(key)

    @abstractmethod
    def encode_vertex_constraint(self) -> list[list[int]]:
        pass

    @abstractmethod
    def encode_distance_constraint(self) -> list[list[int]]:
        pass
