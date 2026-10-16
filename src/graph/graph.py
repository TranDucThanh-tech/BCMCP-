from typing import Iterable

from src.graph.vertex import Vertex
from src.graph.edge import Edge


class Graph:
    def __init__(self, vertices: Iterable[Vertex] = ()):
        self._vertices: dict[int, Vertex] = {}
        self._edges: list[Edge] = []
        self._adjacency: dict[int, list[Edge]] = {}

        for vertex in vertices:
            self.add_vertex(vertex)

    def add_vertex(self, vertex: Vertex) -> None:
        if vertex.id in self._vertices:
            raise ValueError(
                f"Vertex {vertex.id} already exists."
            )

        self._vertices[vertex.id] = vertex
        self._adjacency[vertex.id] = []

    def add_edge(self, u_id: int, v_id: int, weight: int) -> None:
        if u_id == v_id:
            raise ValueError(
                "Self-loops are not supported by add_edge()."
            )

        if u_id not in self._vertices:
            raise ValueError(f"Vertex {u_id} does not exist.")

        if v_id not in self._vertices:
            raise ValueError(f"Vertex {v_id} does not exist.")

        if weight < 0:
            raise ValueError("Edge weight must be non-negative.")

        u = self._vertices[u_id]
        v = self._vertices[v_id]

        edge = Edge(u=u, v=v, weight=weight)

        self._edges.append(edge)
        self._adjacency[u_id].append(edge)
        self._adjacency[v_id].append(edge)

    def get_vertex(self, vertex_id: int) -> Vertex:
        return self._vertices[vertex_id]

    def get_vertices(self) -> list[Vertex]:
        return list(self._vertices.values())

    def get_edges(self) -> list[Edge]:
        return list(self._edges)

    def get_adjacent_edges(self, vertex_id: int) -> list[Edge]:
        if vertex_id not in self._vertices:
            raise ValueError(
                f"Vertex {vertex_id} does not exist."
            )

        return list(self._adjacency[vertex_id])

    def get_neighbors(self, vertex_id: int) -> list[Vertex]:
        neighbors = []

        for edge in self.get_adjacent_edges(vertex_id):
            if edge.u.id == vertex_id:
                neighbors.append(edge.v)
            else:
                neighbors.append(edge.u)

        return neighbors

    def get_vertex_count(self) -> int:
        return len(self._vertices)

    def get_edge_count(self) -> int:
        return len(self._edges)

    def get_max_vertex_weight(self) -> int:
        if not self._vertices:
            return 0

        return max(
            vertex.weight
            for vertex in self._vertices.values()
        )

    def __repr__(self) -> str:
        return (
            f"Graph("
            f"vertices={self.get_vertex_count()}, "
            f"edges={self.get_edge_count()}"
            f")"
        )