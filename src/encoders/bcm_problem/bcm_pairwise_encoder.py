from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.encoders.cardinality.pairwise_encoder import PairwiseEncoder


@BCMEncoderFactory.register("pairwise")
class BCMPairwiseEncoder(BCMEncoder):
    """
    Variable X(v, c): label (largest color) of v equals c, c in [w(v), span].
    Vertex: exactly-one over X(v, .) using pairwise AMO.
    Edge:   forbid every pair of labels (i, j) whose color blocks are too close.
    """

    def __init__(self, bcm_problem: BCMProblem):
        super().__init__(bcm_problem)
        self.cardinality_encoder = PairwiseEncoder(self.vm)
        self.graph = bcm_problem.get_graph()
        self.span = bcm_problem.get_span()

    # ------------------------------------------------------------------ vertices
    def encode_vertex_constraint(self) -> list[list[int]]:
        clauses: list[list[int]] = []

        for vertex in self.graph.get_vertices():
            keys = [("X", vertex.id, c) for c in range(vertex.weight, self.span + 1)]
            clauses.extend(self.cardinality_encoder.encode_exactly_one(keys))

        return clauses

    # ------------------------------------------------------------------ edges
    def encode_distance_constraint(self) -> list[list[int]]:
        """
        u has label i  -> colors [i-w(u)+1, i]
        v has label j  -> colors [j-w(v)+1, j]
        Valid iff  i - j >= b + w(u)   (u above v)
               or  j - i >= b + w(v)   (v above u)
        Otherwise forbid the pair:  (NOT X(u,i)) OR (NOT X(v,j)).
        """
        clauses: list[list[int]] = []

        for edge in self.graph.get_edges():
            u, v, b = edge.u, edge.v, edge.weight

            for i in range(u.weight, self.span + 1):
                for j in range(v.weight, self.span + 1):
                    u_above_v = i - j >= b + u.weight
                    v_above_u = j - i >= b + v.weight
                    if u_above_v or v_above_u:
                        continue
                    clauses.append([
                        -self.get_var(("X", u.id, i)),
                        -self.get_var(("X", v.id, j)),
                    ])

        return clauses