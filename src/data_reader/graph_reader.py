from pathlib import Path

from src.graph.graph import Graph
from src.graph.vertex import Vertex


class GraphReader:
    def __init__(self, file_path: str | Path):
        self._file_path = Path(file_path)

    def read(self) -> Graph:
        if not self._file_path.is_file():
            raise FileNotFoundError(
                f"File not found: {self._file_path}"
            )

        vertex_weights: dict[int, int] = {}
        edge_records: list[tuple[int, int, int]] = []

        expected_vertices = None
        expected_edges = None

        with self._file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split()

                try:
                    record_type = parts[0]
                    if record_type == "c":
                        continue
                    
                    elif record_type == "p":
                        if len(parts) != 4:
                            raise ValueError(
                                "Expected format: p band n m"
                            )

                        if parts[1] != "band":
                            raise ValueError(
                                f"Unsupported graph type: {parts[1]}"
                            )

                        if expected_vertices is not None:
                            raise ValueError(
                                "Duplicate graph header."
                            )

                        expected_vertices = int(parts[2])
                        expected_edges = int(parts[3])

                        if expected_vertices <= 0:
                            raise ValueError(
                                "Vertex count must be positive."
                            )

                        if expected_edges < 0:
                            raise ValueError(
                                "Edge count must be non-negative."
                            )

                    elif record_type == "n":
                        if len(parts) != 3:
                            raise ValueError(
                                "Expected format: n vertex_id weight"
                            )

                        vertex_id = int(parts[1])
                        weight = int(parts[2])

                        if vertex_id <= 0:
                            raise ValueError(
                                "Vertex ID must be positive."
                            )

                        if weight <= 0:
                            raise ValueError(
                                "Vertex weight must be positive."
                            )

                        if vertex_id in vertex_weights:
                            raise ValueError(
                                f"Duplicate vertex: {vertex_id}"
                            )

                        vertex_weights[vertex_id] = weight

                    elif record_type == "e":
                        if len(parts) != 4:
                            raise ValueError(
                                "Expected format: e u v weight"
                            )

                        u = int(parts[1])
                        v = int(parts[2])
                        weight = int(parts[3])

                        if u <= 0 or v <= 0:
                            raise ValueError(
                                "Vertex IDs must be positive."
                            )

                        if weight < 0:
                            raise ValueError(
                                "Edge weight must be non-negative."
                            )

                        edge_records.append((u, v, weight))

                    else:
                        raise ValueError(
                            f"Unknown record type: {record_type}"
                        )

                except (ValueError, IndexError) as exc:
                    raise ValueError(
                        f"Invalid data at line {line_number}: "
                        f"{line}\nReason: {exc}"
                    ) from exc

        if expected_vertices is None:
            raise ValueError("Missing graph header.")

        if len(edge_records) != expected_edges:
            raise ValueError(
                f"Expected {expected_edges} edges, "
                f"but found {len(edge_records)}."
            )

        expected_ids = set(range(1, expected_vertices + 1))

        if set(vertex_weights) != expected_ids:
            raise ValueError(
                "Vertex IDs must be exactly "
                f"1 through {expected_vertices}."
            )

        for u, v, _ in edge_records:
            if u not in expected_ids or v not in expected_ids:
                raise ValueError(
                    f"Edge ({u}, {v}) references an invalid vertex."
                )

        graph = Graph()

        for vertex_id in range(1, expected_vertices + 1):
            graph.add_vertex(
                Vertex(
                    id=vertex_id,
                    weight=vertex_weights[vertex_id]
                )
            )

        for u, v, weight in edge_records:
            if(u == v):
                continue  # Skip self-loops
            graph.add_edge(u, v, weight)

        return graph