import argparse
import time

from src.data_reader.graph_reader import GraphReader

# import để các decorator @register chạy (encoder và solver)
from src.encoders.bcm_problem.bcm_pairwise_encoder import BCMPairwiseEncoder  # noqa: F401
from src.encoders.bcm_problem.bcm_order_encoder import BCMOrderEncoder  # noqa: F401
from src.encoders.bcm_problem.bcm_sequential_counter_encoder import BCMSequentialCounterEncoder  # noqa: F401
import src.solvers.bcm_solver  # noqa: F401  (__init__.py import plain/incremental/maxsat)
from src.solvers.bcm_solver_factory import BCMSolverFactory
from src.solvers.plain_bcm_solver import PlainBCMSolver
from src.solvers.incremental_bcm_solver import IncrementalBCMSolver


# ------------------------------------------------------------------ tiện ích
def timed(func, *args, **kwargs):
    """Chạy func, trả về (kết quả, thời gian CPU tính bằng giây)."""
    start = time.process_time()
    result = func(*args, **kwargs)
    return result, time.process_time() - start


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


# ------------------------------------------------------------------ main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/test.txt")
    parser.add_argument("--encoder", default="sequential_counter")
    parser.add_argument("--solvers", nargs="+", default=["plain", "incremental"])
    parser.add_argument("--sat", default="cadical153", help="tên solver của PySAT")
    parser.add_argument("--ub", type=int, default=None, help="mặc định: UB tham lam")
    parser.add_argument("--lb", type=int, default=None, help="mặc định: LB từ cạnh/đỉnh")
    args = parser.parse_args()

    graph = GraphReader(args.data).read()
    lb = args.lb if args.lb is not None else lower_bound(graph)
    ub = args.ub if args.ub is not None else greedy_ub(graph)

    print(f"Graph : {args.data}")
    print(f"Encoder: {args.encoder} | SAT solver: {args.sat} | LB={lb} UB={ub}")

    rows, spans = [], {}
    for name in args.solvers:
        solver = BCMSolverFactory.create(
            name, graph, args.encoder, ub, lb, sat_solver_name=args.sat
        )
        result, cpu = timed(solver.run)

        if result.span is None:
            status = "INFEASIBLE (UB quá nhỏ)"
        elif not is_valid(graph, result.ends):
            status = "INVALID"
        else:
            status = "valid" + (" & optimal" if result.proven_optimal else "")
            spans[name] = result.span
        rows.append((name, result.span, cpu, status))

    # --- Thống kê ---
    print("\n========================================")
    print("              TIMING REPORT             ")
    print("========================================")
    print(f"{'Solver':<14}{'Span':>6}{'CPU (s)':>12}   Status")
    for name, span, cpu, status in rows:
        print(f"{name:<14}{str(span):>6}{cpu:>12.4f}   {status}")
    print("----------------------------------------")

    if len(set(spans.values())) > 1:
        print(f"CẢNH BÁO: các solver cho span khác nhau: {spans}")
    elif spans:
        print(f"Các solver thống nhất: span = {next(iter(spans.values()))}")
    print("========================================")


if __name__ == "__main__":
    main()