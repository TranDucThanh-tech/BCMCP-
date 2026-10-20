import argparse
import time

from src.data_reader.graph_reader import GraphReader

import src.encoders.bcm_problem                       # noqa: F401  (đăng ký encoder)
from src.solvers import SolverFamilyFactory  



# ------------------------------------------------------------------ tiện ích
def timed(func, *args, **kwargs):
    """Chạy func, trả về (kết quả, CPU time, wall time) tính bằng giây."""
    cpu0, wall0 = time.process_time(), time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.process_time() - cpu0, time.perf_counter() - wall0


def lower_bound(graph) -> int:
    lb = max(v.weight for v in graph.get_vertices())
    for e in graph.get_edges():
        lb = max(lb, e.u.weight + e.v.weight + e.weight)
    return lb


def greedy_ub(graph) -> int:
    """UB hợp lệ: đặt từng đỉnh vào vị trí đầu tiên không xung đột."""
    adj = {v.id: [] for v in graph.get_vertices()}
    for e in graph.get_edges():
        adj[e.u.id].append((e.v, e.weight))
        adj[e.v.id].append((e.u, e.weight))

    ends = {}
    for v in sorted(graph.get_vertices(), key=lambda x: -len(adj[x.id])):
        start = 1
        while True:
            end = start + v.weight - 1
            if all(
                u.id not in ends
                or start - ends[u.id] > w                      # v nằm sau u
                or ends[u.id] - u.weight + 1 - end > w         # v nằm trước u
                for u, w in adj[v.id]
            ):
                ends[v.id] = end
                break
            start += 1
    return max(ends.values())


def is_valid(graph, ends) -> bool:
    """Kiểm tra theo định nghĩa (1) của bài báo, độc lập với encoder."""
    for v in graph.get_vertices():
        if v.id not in ends or ends[v.id] < v.weight:
            return False
    for e in graph.get_edges():
        eu, ev = ends[e.u.id], ends[e.v.id]
        su, sv = eu - e.u.weight + 1, ev - e.v.weight + 1
        if not (sv - eu > e.weight or su - ev > e.weight):
            return False
    return True


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/test.txt")
    parser.add_argument("--solvers", nargs="+",
                        default=["cnf:plain", "cnf:incremental"],
                        help="dạng họ:chiến_lược, ví dụ cnf:incremental cp:cpsat")
    parser.add_argument("--ub", type=int, default=None)
    parser.add_argument("--lb", type=int, default=None)
    parser.add_argument("--list", action="store_true", help="liệt kê họ và chiến lược")
    for family in SolverFamilyFactory.all():          # mỗi họ tự thêm tham số của nó
        family.add_arguments(parser)
    return parser


def main():
    args = build_parser().parse_args()

    if args.list:
        for name in SolverFamilyFactory.names():
            print(f"{name}: {SolverFamilyFactory.get(name).strategies()}")
        return

    graph = GraphReader(args.data).read()
    lb = args.lb if args.lb is not None else lower_bound(graph)
    ub = args.ub if args.ub is not None else greedy_ub(graph)
    print(f"Graph: {args.data} | LB={lb} UB={ub}")

    rows, spans = [], {}
    for spec in args.solvers:
        family, strategy = spec.split(":")
        solver = SolverFamilyFactory.create(family, strategy, graph, ub, lb, args)
        result, cpu, wall = timed(solver.run)

        if result.span is None:
            status = "INFEASIBLE / no solution"
        elif not is_valid(graph, result.ends):
            status = "INVALID"
        else:
            status = "valid" + (" & optimal" if result.proven_optimal else "")
            if result.proven_optimal:
                spans[spec] = result.span
        rows.append((spec, result.span, cpu, wall, status))

    print("\n" + "=" * 62)
    print(f"{'Solver':<20}{'Span':>6}{'CPU (s)':>11}{'Wall (s)':>11}   Status")
    for spec, span, cpu, wall, status in rows:
        print(f"{spec:<20}{str(span):>6}{cpu:>11.4f}{wall:>11.4f}   {status}")
    print("-" * 62)
    if len(set(spans.values())) > 1:
        print(f"CẢNH BÁO: span tối ưu khác nhau: {spans}")
    elif spans:
        print(f"Các solver thống nhất: span = {next(iter(spans.values()))}")
    print("=" * 62)


if __name__ == "__main__":
    main()