from typing import Hashable

from src.variables.variable import Variable


class VariableManager:
    def __init__(self):
        self._next_id = 1

        # Ánh xạ từ khóa sang biến
        self._key_to_variable: dict[Hashable, Variable] = {}

        # Ánh xạ từ SAT ID sang biến
        self._id_to_variable: dict[int, Variable] = {}

    def get_var(self, key: Hashable) -> int:
        """
        Lấy SAT ID của biến tương ứng với key.

        Nếu biến chưa tồn tại, tự động cấp phát ID mới.
        Nếu đã tồn tại, trả về ID cũ.
        """
        if key not in self._key_to_variable:
            variable = Variable(
                id=self._next_id,
                key=key
            )

            self._key_to_variable[key] = variable
            self._id_to_variable[self._next_id] = variable

            self._next_id += 1

        return self._key_to_variable[key].id

    def get_variable(self, var_id: int) -> Variable:
        """
        Lấy thông tin biến từ SAT ID.
        """
        var_id = abs(var_id)

        if var_id not in self._id_to_variable:
            raise KeyError(f"Unknown variable ID: {var_id}")

        return self._id_to_variable[var_id]

    def decode(self, literal: int) -> tuple[bool, Hashable]:
        """
        Giải mã một literal.

        Trả về:
            (True, key)  nếu literal dương.
            (False, key) nếu literal âm.
        """
        variable = self.get_variable(literal)

        return literal > 0, variable.key

    def decode_model(
        self,
        model: list[int]
    ) -> list[tuple[bool, Hashable]]:
        """
        Giải mã toàn bộ model do SAT Solver trả về.
        """
        return [
            self.decode(literal)
            for literal in model
            if literal != 0
        ]
    
    def decode_list(self, var_ids: list[int] | tuple[int, ...]) -> tuple[Hashable, ...]:
        return tuple(
            self.get_variable(var_id).key
            for var_id in var_ids
        )
    
    def num_variables(self) -> int:
        return len(self._id_to_variable)

    def get_all_variables(self) -> list[Variable]:
        return list(self._id_to_variable.values())