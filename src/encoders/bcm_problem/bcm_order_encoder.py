from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.encoders.cardinality.order_encoder import OrderEncoder


@BCMEncoderFactory.register("order")
class BCMOrderEncoder(BCMEncoder):
    """(giữ nguyên docstring)"""

    def __init__(self, bcm_problem: BCMProblem):
        super().__init__(bcm_problem)
        self.order: dict[int, list[int]] = {}
        self.cardinality_encoder = OrderEncoder(self.vm)

    # ------------------------------------------------------------------ vertices
    def encode_vertex_constraint(self) -> list[list[int]]:
        clauses: list[list[int]] = []
        span = self.bcm_problem.get_span()        # horizon = UB

        for vertex in self.bcm_problem.get_graph().get_vertices():
            if span < vertex.weight:
                raise ValueError(
                    f"horizon {span} < weight {vertex.weight} of vertex {vertex.id}"
                )

            keys = [("X", vertex.id, c) for c in range(vertex.weight, span + 1)]
            clauses.extend(self.cardinality_encoder.encode_exactly_one(keys))

            size = len(keys)
            self.order[vertex.id] = [
                self.get_var(("G", tuple(keys), i)) for i in range(1, size + 2)
            ]

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
                if upper < span:
                    clause.append(-self.le(other, upper))
                if lower >= other.weight:
                    clause.append(self.le(other, lower))
                clauses.append(clause)

        return clauses

    # ------------------------------------------------------------------ incremental
    def span_assumptions(self, k: int) -> list[int] | None:
        """span <= k  <=>  NOT G_{k-w+2} với mọi v."""
        top = self.bcm_problem.get_span()
        if k >= top:
            return []

        lits: list[int] = []
        for vertex in self.bcm_problem.get_graph().get_vertices():
            if k < vertex.weight:
                return None
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
        """Literal for 'label(vertex) <= label' = NOT G_{label - w + 2}."""
        g = self.order[vertex.id]
        index = label - vertex.weight + 1          # position of G_{label-w+2} in the list
        if not 0 <= index < len(g):
            raise ValueError(
                f"no order variable for label {label} of vertex {vertex.id} "
                f"(valid labels {vertex.weight}..{vertex.weight + len(g) - 2})"
            )
        return -g[index]