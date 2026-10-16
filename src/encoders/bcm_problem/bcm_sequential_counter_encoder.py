from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.encoders.cardinality.sequential_counter_encoder import SequentialCounterEncoder


@BCMEncoderFactory.register("sequential_counter")
class BCMSequentialCounterEncoder(BCMEncoder):
    def __init__(self, bcm_problem: BCMProblem):
        super().__init__(bcm_problem)
        self.prefix: dict[int, list[int]] = {}
        self.cardinality_encoder = SequentialCounterEncoder(self.vm)

    # ------------------------------------------------------------------ vertices
    def encode_vertex_constraint(self) -> list[list[int]]:
        clauses: list[list[int]] = []
        span = self.bcm_problem.get_span()

        for vertex in self.bcm_problem.get_graph().get_vertices():
            if span < vertex.weight:
                clauses.append([])
                self.prefix[vertex.id] = []
                continue

            keys = [("X", vertex.id, color) for color in range(vertex.weight, span + 1)]
            vertex_clauses, prefix = self.cardinality_encoder.encode_exactly_one_with_prefix(keys)
            clauses.extend(vertex_clauses)
            self.prefix[vertex.id] = prefix

        return clauses

    # ------------------------------------------------------------------ edges
    def encode_distance_constraint(self) -> list[list[int]]:
        clauses: list[list[int]] = []
        span = self.bcm_problem.get_span()

        for edge in self.bcm_problem.get_graph().get_edges():
            reference, other = (
                (edge.u, edge.v) if edge.u.weight > edge.v.weight else (edge.v, edge.u)
            )

            # An empty domain (span < weight) already makes the formula UNSAT.
            if span < reference.weight or span < other.weight:
                continue

            d_ro = edge.weight + other.weight
            d_or = edge.weight + reference.weight

            for label in range(reference.weight, span + 1):
                x = self.get_var(("X", reference.id, label))

                upper = min(label + d_ro - 1, span)
                lower = label - d_or

                clause = [-x]

                # not P(o, upper); P(o, span) is always true, so skip it.
                if upper < span:
                    clause.append(-self.le(other, upper))

                # P(o, lower); if lower < w(o) it is the constant False, so skip it.
                if lower >= other.weight:
                    clause.append(self.le(other, lower))

                clauses.append(clause)

        return clauses

    # ------------------------------------------------------------------ helpers
    def le(self, vertex, label: int) -> int:
        prefix = self.prefix[vertex.id]
        index = label - vertex.weight
        if not 0 <= index < len(prefix):
            raise ValueError(
                f"no prefix variable for label {label} of vertex {vertex.id} "
                f"(valid labels {vertex.weight}..{vertex.weight + len(prefix) - 1})"
            )
        return prefix[index]