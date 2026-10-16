from typing import Hashable

from src.encoders.cardinality.cardinality_encoder import (
    CardinalityEncoder
)


class PairwiseEncoder(CardinalityEncoder):

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

        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                clauses.append([
                    -variables[i],
                    -variables[j]
                ])

        return clauses