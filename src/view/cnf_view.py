from src.variables.variable_manager import VariableManager


class CNFView:

  def __init__(self, variable_manager: VariableManager):
    self.vm = variable_manager

  def show_literal(self, literal: int) -> str:
    variable = self.vm.get_variable(abs(literal))
    key = variable.key

    name = self._format_key(key)

    if literal < 0:
      return f"¬{name}"

    return name

  def _format_key(self, key) -> str:
    if isinstance(key, tuple):
      # Xử lý biến X: ('X', vertex_id, color)
      if key[0] == "X" or key[0] == "G":
        _, vertex_id, color = key
        return f"X[{vertex_id}, {color}]"

      # Xử lý biến phụ trợ của sequential counter: ('SEQ', sequence_tuple)
      if key[0] == "SEQ":
        _, sequence = key
        elements = ", ".join(self._format_key(item) for item in sequence)
        return f"SEQ[{{{elements}}}]"

    return str(key)

  def show_clause(self, clause: list[int]) -> str:
    if not clause:
      return "()"

    literals = [self.show_literal(literal) for literal in clause]

    return "(" + " ∨ ".join(literals) + ")"

  def show(self, cnf: list[list[int]]) -> None:
    print("CNF Formula")
    print("-" * 80)

    for index, clause in enumerate(cnf, start=1):
      print(f"C{index}: {self.show_clause(clause)}")

    print("-" * 80)

  @staticmethod
  def show_statistics(cnf: list[list[int]]) -> None:
    num_clauses = len(cnf)
    num_literals = sum(len(clause) for clause in cnf)

    print(f"Number of clauses: {num_clauses}")
    print(f"Number of literals: {num_literals}")