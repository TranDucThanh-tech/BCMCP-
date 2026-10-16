from typing import Hashable

from src.encoders.cardinality.cardinality_encoder import CardinalityEncoder


class SequentialCounterEncoder(CardinalityEncoder):
    
    def _ladder(self, keys: list[Hashable]) -> tuple[list[list[int]], list[int]]:
        x = [self.get_var(key) for key in keys]
        size = len(x)

        prefix = [x[0]]
        for i in range(1, size - 1):
            prefix.append(self.get_var(("SEQ", keys[0], keys[i])))

        clauses: list[list[int]] = []

        # P_i <=> x_i or P_{i-1}   (for 1 <= i <= n-2)
        for i in range(1, size - 1):
            clauses.append([-x[i], prefix[i]])                 # x_i       -> P_i
            clauses.append([-prefix[i - 1], prefix[i]])        # P_{i-1}   -> P_i
            clauses.append([x[i], prefix[i - 1], -prefix[i]])  # P_i       -> x_i or P_{i-1}

        # at most one: x_i excludes everything before it
        for i in range(1, size):
            clauses.append([-x[i], -prefix[i - 1]])

        return clauses, prefix

    # ------------------------------------------------------------------ public
    def encode_alo(self, keys: list[Hashable]) -> list[list[int]]:
        variables = [self.get_var(key) for key in keys]
        return [variables] if variables else [[]]

    def encode_amo(self, keys: list[Hashable]) -> list[list[int]]:
        if len(keys) <= 1:
            return []
        clauses, _ = self._ladder(keys)
        return clauses

    def encode_exactly_one(self, keys: list[Hashable]) -> list[list[int]]:
        clauses, _ = self.encode_exactly_one_with_prefix(keys)
        return clauses

    def encode_exactly_one_with_prefix(
        self, keys: list[Hashable]
    ) -> tuple[list[list[int]], list[int]]:
    
        size = len(keys)

        if size == 0:
            return [[]], []                      # no value possible -> UNSAT

        if size == 1:
            return [[self.get_var(keys[0])]], []  # unit clause

        clauses, prefix = self._ladder(keys)
        # at least one: x_{n-1} or one of the earlier ones
        clauses.append([prefix[size - 2], self.get_var(keys[size - 1])])
        return clauses, prefix