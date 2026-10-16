from dataclasses import dataclass

from src.graph.vertex import Vertex


@dataclass(frozen=True, slots=True)
class Edge:
    u: Vertex
    v: Vertex
    weight: int