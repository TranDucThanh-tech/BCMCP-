from src.bcm.bcm_problem import BCMProblem

class BCMEncoderFactory:
  _registry = {}

  @classmethod
  def register(cls, name: str):
    """Decorator chỉ nhận vào tên của encoder"""

    def decorator(encoder_cls):
      cls._registry[name.lower()] = encoder_cls
      return encoder_cls

    return decorator

  @classmethod
  def create(cls, name: str, bcm_problem: BCMProblem):
    """Khởi tạo encoder tương ứng và truyền bcm_problem vào"""
    encoder_cls = cls._registry.get(name.lower())
    if not encoder_cls:
      raise ValueError(f"Không tìm thấy encoder với tên: '{name}'")

    # Khởi tạo đối tượng encoder
    return encoder_cls(bcm_problem)