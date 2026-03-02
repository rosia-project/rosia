from typing import TypeVar, Generic

T = TypeVar("T")


class ObjectProxy(Generic[T]):
    """A transparent proxy that delegates all attribute access to a wrapped object.

    The wrapped object can be swapped at any time via ``set_target()``,
    making this useful for stable module-level references that need to
    point at different underlying instances over time.
    """

    def __init__(self, target: T) -> None:
        object.__setattr__(self, "_target", target)

    def set_target(self, target: T) -> None:
        object.__setattr__(self, "_target", target)

    def __getattr__(self, name: str) -> object:
        return getattr(object.__getattribute__(self, "_target"), name)

    def __setattr__(self, name: str, value: object) -> None:
        setattr(object.__getattribute__(self, "_target"), name, value)
