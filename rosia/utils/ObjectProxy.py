import importlib
from typing import TypeVar, Generic

T = TypeVar("T")


def _resolve_proxy(module_name: str, attr_name: str) -> object:
    mod = importlib.import_module(module_name)
    return getattr(mod, attr_name)


class ObjectProxy(Generic[T]):
    """A transparent proxy that delegates all attribute access to a wrapped object.

    The wrapped object can be swapped at any time via ``set_target()``,
    making this useful for stable module-level references that need to
    point at different underlying instances over time.

    When *module* and *attr* are provided, pickling resolves back to
    the module-level attribute instead of creating a detached copy.
    """

    def __init__(self, target: T, *, module: str = "", attr: str = "") -> None:
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_module", module)
        object.__setattr__(self, "_attr", attr)

    def set_target(self, target: T) -> None:
        object.__setattr__(self, "_target", target)

    def __reduce__(self):
        module = object.__getattribute__(self, "_module")
        attr = object.__getattribute__(self, "_attr")
        if module and attr:
            return (_resolve_proxy, (module, attr))
        return (ObjectProxy, (object.__getattribute__(self, "_target"),))

    def __getattr__(self, name: str) -> object:
        return getattr(object.__getattribute__(self, "_target"), name)

    def __setattr__(self, name: str, value: object) -> None:
        setattr(object.__getattribute__(self, "_target"), name, value)


class FunctionProxy:
    """A transparent proxy for a callable that can be swapped at runtime.

    Useful for stable module-level function references that need to point at
    different underlying callables over time (e.g. a function that becomes
    bound to a node runtime once one exists).
    """

    def __init__(self, target=None, *, module: str = "", attr: str = "") -> None:
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_module", module)
        object.__setattr__(self, "_attr", attr)

    def set_target(self, target) -> None:
        object.__setattr__(self, "_target", target)

    def __call__(self, *args, **kwargs):
        target = object.__getattribute__(self, "_target")
        if target is None:
            raise RuntimeError("FunctionProxy target is not set")
        return target(*args, **kwargs)

    def __reduce__(self):
        module = object.__getattribute__(self, "_module")
        attr = object.__getattribute__(self, "_attr")
        if module and attr:
            return (_resolve_proxy, (module, attr))
        return (FunctionProxy, (object.__getattribute__(self, "_target"),))
