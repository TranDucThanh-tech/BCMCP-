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
        span = self.bcm_problem.get_span()   # horizon = UB

        for vertex in self.bcm_problem.get_graph().get_vertices():
            if span < vertex.weight:
                # Horizon nhỏ hơn weight: UB không hợp lệ, không nên nhét [] vào solver
                raise ValueError(
                    f"horizon {span} < weight {vertex.weight} of vertex {vertex.id}"
                )

            keys = [("X", vertex.id, c) for c in range(vertex.weight, span + 1)]
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

            d_ro = edge.weight + other.weight
            d_or = edge.weight + reference.weight

            for label in range(reference.weight, span + 1):
                x = self.get_var(("X", reference.id, label))

                upper = min(label + d_ro - 1, span)
                lower = label - d_or

                clause = [-x]
                if upper < span:                      # P(o, span) luôn true
                    clause.append(-self.le(other, upper))
                if lower >= other.weight:             # dưới weight thì là False
                    clause.append(self.le(other, lower))

                clauses.append(clause)

        return clauses

    # ------------------------------------------------------------------ incremental
    def span_assumptions(self, k: int) -> list[int] | None:
        """span <= k  <=>  le(v, k) với mọi v (màu cuối của v <= k)."""
        top = self.bcm_problem.get_span()
        if k >= top:
            return []                                  # không cần ràng buộc gì thêm

        lits: list[int] = []
        for vertex in self.bcm_problem.get_graph().get_vertices():
            if k < vertex.weight:
                return None                            # đỉnh này không thể kết thúc <= k
            lits.append(self.le(vertex, k))
        return lits

    def decode_ends(self, model: set[int]) -> dict[int, int]:
        span = self.bcm_problem.get_span()
        ends: dict[int, int] = {}
        for vertex in self.bcm_problem.get_graph().get_vertices():
            for c in range(vertex.weight, span + 1):
                if self.get_var(("X", vertex.id, c)) in model:
                    ends[vertex.id] = c
                    break
        return ends

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