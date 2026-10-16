from typing import Hashable

from src.encoders.cardinality.cardinality_encoder import (
    CardinalityEncoder
)


class SequentialCounterEncoder(CardinalityEncoder):

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
        variables = [self.get_var(key) for key in keys]
        clauses = []
        size = len(variables)

        if size <= 1:
            return clauses

        # Key của biến phụ là chuỗi key của các biến mà nó đại diện.
        def seq_var(prefix: tuple[Hashable, ...]) -> int:
            if len(prefix) == 1:
                return self.get_var(prefix[0])
            return self.get_var(("SEQ", prefix))

        # Liên kết biến đầu vào với biến phụ.
        for i in range(1, size):
            clauses.append([
                -variables[i],
                seq_var(tuple(keys[:i + 1]))
            ])

        # Liên kết các biến phụ liên tiếp.
        for i in range(size - 1):
            clauses.append([
                -seq_var(tuple(keys[:i + 1])),
                seq_var(tuple(keys[:i + 2]))
            ])

        # Liên kết ngược giữa biến đầu vào và biến phụ.
        for i in range(size - 1, 0, -1):
            clauses.append([
                variables[i],
                seq_var(tuple(keys[:i])),
                -seq_var(tuple(keys[:i + 1]))
            ])

        # Ngăn hai biến đầu vào cùng đúng.
        for i in range(size - 1, 0, -1):
            clauses.append([
                -variables[i],
                -seq_var(tuple(keys[:i]))
            ])

        return clauses

    def encode_exactly_one(
        self,
        keys: list[Hashable]
    ) -> list[list[int]]:
        variables = [self.get_var(key) for key in keys]
        clauses = []
        size = len(variables)

        if size < 1:
            return [[]]

        if size == 1:
            return [variables]

        # Key của biến phụ là chuỗi key của các biến mà nó đại diện.
        def seq_var(prefix: tuple[Hashable, ...]) -> int:
            if len(prefix) == 1:
                return self.get_var(prefix[0])

            return self.get_var(("SEQ", prefix))

        # Liên kết biến đầu vào với biến phụ.
        for i in range(1, size):
            clauses.append([
                -variables[i],
                seq_var(tuple(keys[:i + 1]))
            ])

        # Liên kết các biến phụ liên tiếp.
        for i in range(size - 1):
            clauses.append([
                -seq_var(tuple(keys[:i + 1])),
                seq_var(tuple(keys[:i + 2]))
            ])

        # Liên kết ngược giữa biến đầu vào và biến phụ.
        for i in range(size - 1, 0, -1):
            clauses.append([
                variables[i],
                seq_var(tuple(keys[:i])),
                -seq_var(tuple(keys[:i + 1]))
            ])

        # Ngăn hai biến đầu vào cùng đúng.
        for i in range(size - 1, 0, -1):
            clauses.append([
                -variables[i],
                -seq_var(tuple(keys[:i]))
            ])

        # Thêm điều kiện ít nhất một biến đầu vào đúng.
        clauses.append([
            seq_var(tuple(keys[:size - 1])),
            variables[size - 1]
        ])

        return clauses
