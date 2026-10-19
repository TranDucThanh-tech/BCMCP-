from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.encoders.cardinality.order_encoder import OrderEncoder


@BCMEncoderFactory.register("order")
class BCMOrderEncoder(BCMEncoder):
    """
    X(v, c): label of v equals c, c in [w(v), span]
    G(v, i): order variable of OrderEncoder, i in 1..size+1 (size = span - w(v) + 1)
             G_i  <=>  label(v) >= w(v) + i - 1
    label(v) <= a  <=>  NOT G_{a - w(v) + 2}
    """

    def __init__(self, bcm_problem: BCMProblem):
        super().__init__(bcm_problem)
        self.order: dict[int, list[int]] = {}   # vertex.id -> [G_1, ..., G_{size+1}]
        self.cardinality_encoder = OrderEncoder(self.vm)

    # ------------------------------------------------------------------ vertices
    def encode_vertex_constraint(self) -> list[list[int]]:
        clauses: list[list[int]] = []
        span = self.bcm_problem.get_span()

        for vertex in self.bcm_problem.get_graph().get_vertices():
            if span < vertex.weight:
                clauses.append([])
                self.order[vertex.id] = []
                continue

            keys = [("X", vertex.id, color) for color in range(vertex.weight, span + 1)]
            clauses.extend(self.cardinality_encoder.encode_exactly_one(keys))

            # Same key format as OrderEncoder uses, so ids come from the shared vm.
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

                # other is NOT entirely <= upper (i.e. other above reference).
                # label(o) <= span is always true, so skip when upper == span.
                if upper < span:
                    clause.append(-self.le(other, upper))

                # other entirely <= lower (other below reference).
                # If lower < w(o) it is the constant False, so skip it.
                if lower >= other.weight:
                    clause.append(self.le(other, lower))

                clauses.append(clause)

        return clauses

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