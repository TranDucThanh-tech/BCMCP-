from src.bcm.bcm_problem import BCMProblem
from src.encoders.bcm_problem.bcm_encoder import BCMEncoder
from src.encoders.bcm_problem.bcm_encoder_factory import BCMEncoderFactory
from src.encoders.cardinality.pairwise_encoder import PairwiseEncoder


@BCMEncoderFactory.register("pairwise")
class BCMPairwiseEncoder(BCMEncoder):
    """
    Variable X(v, c): label (largest color) of v equals c, c in [w(v), span].
    Variable U(k):    every vertex has label <= k, k in [max_w, span-1]
                      (chỉ dùng cho incremental).
    Vertex: exactly-one over X(v, .) using pairwise AMO.
    Edge:   forbid every pair of labels (i, j) whose color blocks are too close.
    """

    def __init__(self, bcm_problem: BCMProblem):
        super().__init__(bcm_problem)
        self.cardinality_encoder = PairwiseEncoder(self.vm)
        self.graph = bcm_problem.get_graph()
        self.span = bcm_problem.get_span()          # horizon = UB
        self.max_weight = max(v.weight for v in self.graph.get_vertices())

    # ------------------------------------------------------------------ vertices
    def encode_vertex_constraint(self) -> list[list[int]]:
        clauses: list[list[int]] = []

        for vertex in self.graph.get_vertices():
            if self.span < vertex.weight:
                raise ValueError(
                    f"horizon {self.span} < weight {vertex.weight} of vertex {vertex.id}"
                )
            keys = [("X", vertex.id, c) for c in range(vertex.weight, self.span + 1)]
            clauses.extend(self.cardinality_encoder.encode_exactly_one(keys))

        return clauses

    # ------------------------------------------------------------------ edges
    def encode_distance_constraint(self) -> list[list[int]]:
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

    # ------------------------------------------------------------------ incremental
    def encode_bound_constraint(self) -> list[list[int]]:
        """U(k) -> not X(v, k+1) với mọi v;  U(k) -> U(k+1).
        Chỉ tạo U(k) cho k trong [max_w, span-1]: với k < max_w thì
        span_assumptions trả None nên U(k) không bao giờ được dùng."""
        clauses: list[list[int]] = []
        vertices = self.graph.get_vertices()

        for k in range(self.max_weight, self.span):
            u_k = self.get_var(("U", k))
            for vertex in vertices:                 
                clauses.append([-u_k, -self.get_var(("X", vertex.id, k + 1))])
            if k + 1 < self.span:
                clauses.append([-u_k, self.get_var(("U", k + 1))])

        return clauses

    def span_assumptions(self, k: int) -> list[int] | None:
        """span <= k  <=>  U(k)."""
        if k >= self.span:
            return []                                # không cần ràng buộc thêm
        if k < self.max_weight:
            return None                              # có đỉnh không thể kết thúc <= k
        return [self.get_var(("U", k))]              # đã tạo ở encode_bound_constraint

    def decode_ends(self, model: set[int]) -> dict[int, int]:
        ends: dict[int, int] = {}
        for vertex in self.graph.get_vertices():
            for c in range(vertex.weight, self.span + 1):
                if self.get_var(("X", vertex.id, c)) in model:
                    ends[vertex.id] = c
                    break
        return ends