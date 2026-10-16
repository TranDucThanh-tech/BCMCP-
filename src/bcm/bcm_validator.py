from src.bcm.bcm_problem import BCMProblem


class BCMValidator:
    """
    Validate a SAT model against the *definition* of the Bandwidth Consecutive
    Multicoloring Problem (it does not reuse the encoder's formulas).

    Label of a vertex v = the largest color e(v) of v. Its color set is the
    consecutive block {e(v) - w(v) + 1, ..., e(v)}.
    For every edge (u, v) with weight b:  |x - y| > b  for every color x of u and y of v.
    """

    MAX_PRINTED_ERRORS = 20

    def __init__(self, model: list[int], bcm_problem: BCMProblem, vm, verbose: bool = False) -> None:
        """
        :param model: literals returned by the SAT solver (e.g. solver.get_model()).
        :param bcm_problem: problem instance (graph, span, vertex/edge weights).
        :param vm: variable manager mapping tuple keys to SAT variable ids.
        :param verbose: print every vertex / edge that is checked.
        """
        self.model_set = set(model) if model else set()
        self.bcm_problem = bcm_problem
        self.graph = bcm_problem.get_graph()
        self.span = bcm_problem.get_span()
        self.vm = vm
        self.verbose = verbose

        self.errors: list[str] = []
        self.vertex_labels: dict[int, int] = {}
        self.multi_labels: dict[int, list[int]] = {}
        self._extract_vertex_labels()

    # ------------------------------------------------------------------ helpers
    def _var_id(self, key):
        """Look up a variable id WITHOUT creating a new variable when possible."""
        obj2id = getattr(self.vm, "obj2id", None)  # pysat IDPool
        if obj2id is not None:
            return obj2id.get(key)
        return self.vm.get_var(key)

    def _extract_vertex_labels(self) -> None:
        """
        For each vertex collect ALL colors whose X variable is true.
        Exactly one is expected: more than one is recorded in `multi_labels`.
        """
        for vertex in self.graph.get_vertices():
            true_colors = []
            for color in range(vertex.weight, self.span + 1):
                var_id = self._var_id(("X", vertex.id, color))
                if var_id is not None and var_id in self.model_set:
                    true_colors.append(color)

            if len(true_colors) == 1:
                self.vertex_labels[vertex.id] = true_colors[0]
            elif len(true_colors) > 1:
                self.multi_labels[vertex.id] = true_colors

    @staticmethod
    def _color_range(label: int, weight: int) -> range:
        return range(label - weight + 1, label + 1)

    def _report(self, message: str) -> None:
        self.errors.append(message)

    # ------------------------------------------------------------------ checks
    def check_vertex_constraints(self) -> bool:
        """Every vertex has exactly one label, and the label lies in [weight, span]."""
        print("=== Checking Vertex Constraints (Exactly One) ===")
        before = len(self.errors)

        for vertex in self.graph.get_vertices():
            v_id = vertex.id

            if v_id in self.multi_labels:
                self._report(
                    f"Vertex {v_id} has several true labels {self.multi_labels[v_id]} "
                    f"(at-most-one violated)."
                )
                continue

            if v_id not in self.vertex_labels:
                self._report(f"Vertex {v_id} has no label (at-least-one violated).")
                continue

            label = self.vertex_labels[v_id]
            if not (vertex.weight <= label <= self.span):
                self._report(
                    f"Vertex {v_id} has label {label} outside "
                    f"[{vertex.weight}, {self.span}]."
                )
                continue

            if self.verbose:
                colors = self._color_range(label, vertex.weight)
                print(f"[OK] Vertex {v_id}: label = {label}, colors = {colors.start}..{colors.stop - 1}")

        ok = len(self.errors) == before
        print("[PASS] Vertex constraints satisfied." if ok else "[FAIL] Vertex constraints violated.")
        return ok

    def check_distance_constraints(self) -> bool:
        """For every edge, all pairs of colors must differ by MORE than the edge weight."""
        print("=== Checking Distance Constraints ===")
        before = len(self.errors)

        for edge in self.graph.get_edges():
            u, v, b = edge.u, edge.v, edge.weight

            u_label = self.vertex_labels.get(u.id)
            v_label = self.vertex_labels.get(v.id)
            if u_label is None or v_label is None:
                # Already reported by the vertex check; cannot verify this edge.
                self._report(f"Edge ({u.id}, {v.id}) cannot be checked: missing label.")
                continue

            u_colors = self._color_range(u_label, u.weight)
            v_colors = self._color_range(v_label, v.weight)

            bad_pair = next(
                ((x, y) for x in u_colors for y in v_colors if abs(x - y) <= b),
                None,
            )

            if self.verbose:
                print(
                    f"[CHECK] Edge ({u.id}, {v.id}) b={b} | "
                    f"u colors {u_colors.start}..{u_colors.stop - 1}, "
                    f"v colors {v_colors.start}..{v_colors.stop - 1}"
                )

            if bad_pair is not None:
                x, y = bad_pair
                self._report(
                    f"Edge ({u.id}, {v.id}) with b={b}: colors {x} (of {u.id}) and "
                    f"{y} (of {v.id}) differ by {abs(x - y)} <= {b}."
                )

        ok = len(self.errors) == before
        print("[PASS] Distance constraints satisfied." if ok else "[FAIL] Distance constraints violated.")
        return ok

    def check_span(self) -> bool:
        """The largest used color must not exceed the span, and all colors must be >= 1."""
        print("=== Checking Span ===")
        before = len(self.errors)

        for vertex in self.graph.get_vertices():
            label = self.vertex_labels.get(vertex.id)
            if label is None:
                continue
            lowest = label - vertex.weight + 1
            if lowest < 1:
                self._report(f"Vertex {vertex.id} uses color {lowest} < 1.")
            if label > self.span:
                self._report(f"Vertex {vertex.id} uses color {label} > span {self.span}.")

        ok = len(self.errors) == before
        if ok:
            print(f"[PASS] Used span = {self.actual_span()} (limit {self.span}).")
        else:
            print("[FAIL] Span constraints violated.")
        return ok

    def actual_span(self) -> int | None:
        """Largest color actually used by the decoded labels."""
        return max(self.vertex_labels.values()) if self.vertex_labels else None

    # ------------------------------------------------------------------ driver
    def run_all_tests(self) -> bool:
        """Run every check (without stopping at the first failure) and print a summary."""
        print("========================================")
        print("         STARTING BCM SOLUTION TEST     ")
        print("========================================")

        if not self.model_set:
            print("[FAIL] Model is empty or SAT solver returned None (UNSAT).")
            return False

        self.errors.clear()
        results = [
            self.check_vertex_constraints(),
            self.check_distance_constraints(),
            self.check_span(),
        ]

        if self.errors:
            print(f"\n{len(self.errors)} problem(s) found:")
            for message in self.errors[: self.MAX_PRINTED_ERRORS]:
                print(f"  - {message}")
            hidden = len(self.errors) - self.MAX_PRINTED_ERRORS
            if hidden > 0:
                print(f"  ... and {hidden} more.")

        passed = all(results)
        print("========================================")
        print("ALL TESTS PASSED" if passed else "TESTS FAILED")
        print("========================================")
        return passed