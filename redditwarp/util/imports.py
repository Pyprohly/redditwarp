
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec

import sys
import importlib.util

def load_module_from_spec(spec: ModuleSpec) -> ModuleType:
    if spec.loader is None:
        raise ImportError('spec has no loader')

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LazyImport:
    """An object for lazily loading modules."""

    def __call__(self, name: str, package: Optional[str] = None) -> ModuleType:
        try:
            return sys.modules[name]
        except KeyError:
            spec = importlib.util.find_spec(name, package)
            if spec is None:
                raise ImportError(f'module named {name!r} not found')
            if spec.loader is None:
                raise ImportError('spec has no loader')

            module = importlib.util.module_from_spec(spec)
            loader = importlib.util.LazyLoader(spec.loader)
            loader.exec_module(module)
            sys.modules[spec.name] = module
            return module

    def __mod__(self, other: str) -> None:
        if '.' in other:
            raise ValueError('dotted module name not supported')

        module = self(other)
        caller_frame = sys._getframe(1)  # type: ignore
        caller_frame.f_globals[other] = module

lazy_import: LazyImport = LazyImport()
