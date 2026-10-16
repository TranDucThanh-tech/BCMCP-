from typing import Hashable

from src.encoders.cardinality.cardinality_encoder import (
    CardinalityEncoder
)

class OrderEncoder(CardinalityEncoder):

    def encode_alo(
        self,
        keys: list[Hashable]
    ) -> list[list[int]]:
        variables = [self.get_var(key) for key in keys]

        return [variables] if variables else [[]]

    def encode_amo( 
        self,
        keys: list[Hashable]
    ) -> list[list[int]]:
        size = len(keys)
        
        if size == 0:
            return [[]]

        variables = [self.get_var(key) for key in keys]

        def g_var(i: int) -> int:
            return self.get_var(("G", tuple(keys), i))

        clauses = []

        # 1. Định nghĩa tương đương: X_i <-> (G_i AND NOT G_{i+1})
        for i in range(1, size + 1):
            x = variables[i - 1]
            g_i = g_var(i)
            g_next = g_var(i + 1)

            clauses.append([-x, g_i])
            clauses.append([-x, -g_next])
            clauses.append([-g_i, g_next, x])

        # 2. Tính đơn điệu: G_{i+1} -> G_i (tương đương [-g_next, g_i])
        for i in range(1, size + 1):
            clauses.append([-g_var(i + 1), g_var(i)])

        return clauses

    def encode_exactly_one(
        self,
        keys: list[Hashable],
    ) -> list[list[int]]:
        size = len(keys)

        if size == 0:
            return [[]]

        variables = [self.get_var(key) for key in keys]

        def g_var(i: int) -> int:
            return self.get_var(("G", tuple(keys), i))

        clauses = []

        # 1. Định nghĩa tương đương: X_i <-> (G_i AND NOT G_{i+1})
        for i in range(1, size + 1):
            x = variables[i - 1]
            g_i = g_var(i)
            g_next = g_var(i + 1)

            clauses.append([-x, g_i])
            clauses.append([-x, -g_next])
            clauses.append([-g_i, g_next, x])

        # 2. Tính đơn điệu: G_{i+1} -> G_i (tương đương [-g_next, g_i])
        for i in range(1, size + 1):
            clauses.append([-g_var(i + 1), g_var(i)])

        # 3. Điều kiện biên: G_1 luôn đúng và G_{size+1} luôn sai
        clauses.append([g_var(1)])
        clauses.append([-g_var(size + 1)])

        return clauses