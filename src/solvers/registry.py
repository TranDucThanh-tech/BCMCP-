class Registry:
    """Lớp nền: mỗi lớp con có registry riêng, không dùng chung dict."""
    _registry: dict = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry = {}

    @classmethod
    def register(cls, name: str):
        def decorator(item):
            cls._registry[name.lower()] = item
            return item
        return decorator

    @classmethod
    def get(cls, name: str):
        item = cls._registry.get(name.lower())
        if item is None:
            raise ValueError(
                f"'{name}' không có trong {cls.__name__}. Hiện có: {cls.names()}")
        return item

    @classmethod
    def names(cls) -> list[str]:
        return sorted(cls._registry)

    @classmethod
    def all(cls) -> list:
        return list(cls._registry.values())