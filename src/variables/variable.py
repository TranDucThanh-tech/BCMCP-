from dataclasses import dataclass
from typing import Hashable


@dataclass(frozen=True)
class Variable:
    """
    Biểu diễn một biến SAT.

    id:
        Số nguyên dương dùng trong công thức CNF.

    key:
        Thông tin nhận diện biến trong bài toán.
    """
    id: int
    key: Hashable