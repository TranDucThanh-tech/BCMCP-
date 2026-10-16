from typing import Hashable

from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.encoders.cardinality.sequential_counter_encoder import SequentialCounterEncoder


@BCMEncoderFactory.register("sequential_counter")
class BCMSequentialCounterEncoder(BCMEncoder):
    def __init__(self, bcm_problem: BCMProblem):
        super().__init__(bcm_problem)
        self.variables: dict[int, list[tuple]] = {}
        self.cardinality_encoder = SequentialCounterEncoder(self.vm)

    def encode_vertex_constraint(self) -> list[list[int]]:
        clauses = []
        span = self.bcm_problem.get_span()

        for vertex in self.bcm_problem.get_graph().get_vertices():
            keys = [("X", vertex.id, color) for color in range(vertex.weight, span + 1)]
            self.variables[vertex.id] = keys

            if not keys:
                # span < weight: the vertex cannot be placed -> UNSAT.
                # Emit the empty clause explicitly instead of relying on the cardinality encoder.
                clauses.append([])
                continue

            clauses.extend(self.cardinality_encoder.encode_exactly_one(keys))
        return clauses

    def encode_distance_constraint(self) -> list[list[int]]:
        clauses = []
        span = self.bcm_problem.get_span()

        def get_prefix(vertex, label: int) -> tuple:
            # keys of a vertex are consecutive labels starting at vertex.weight,
            # so the position of `label` is computed directly (no list.index scan).
            keys = self.variables[vertex.id]
            index = label - vertex.weight
            return tuple(keys[:index + 1])

        for edge in self.bcm_problem.get_graph().get_edges():
            reference, other = (
                (edge.u, edge.v) if edge.u.weight > edge.v.weight else (edge.v, edge.u)
            )

            # An empty domain already makes the formula UNSAT (empty clause above).
            if not self.variables[reference.id] or not self.variables[other.id]:
                continue

            d_ro = edge.weight + other.weight
            d_or = edge.weight + reference.weight

            for label in range(reference.weight, span + 1):
                x = self.get_var(("X", reference.id, label))

                upper = min(label + d_ro - 1, span)
                lower = label - d_or

                clause = [-x]

                # NOT P(other, upper). P(other, span) is always true -> literal is False, skip it.
                if upper < span:
                    clause.append(-self.seq_var(get_prefix(other, upper)))

                # P(other, lower). If lower < other.weight it is the constant False
                # (no valid label <= lower), so nothing is appended and the clause
                # reduces to forbidding X(reference, label).
                if lower >= other.weight:
                    clause.append(self.seq_var(get_prefix(other, lower)))

                clauses.append(clause)

        return clauses

    def seq_var(self, prefix: tuple[Hashable, ...]) -> int:
        if len(prefix) == 1:
            return self.get_var(prefix[0])

        return self.get_var(("SEQ", prefix))