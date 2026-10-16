from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Vertex:
    id: int
    weight: int