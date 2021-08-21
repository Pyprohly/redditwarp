
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec

import sys
import importlib.util
from importlib.abc import Loader

def load_module_from_spec(spec: ModuleSpec) -> ModuleType:
    if spec.loader is None:
        raise ImportError('spec has no loader')
    assert isinstance(spec.loader, Loader)

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class _LazyImport:
    def __call__(self, name: str, package: Optional[str] = None) -> ModuleType:
        try:
            module = sys.modules[name]
        except KeyError:
            spec = importlib.util.find_spec(name, package)
            if spec is None:
                raise ImportError(f'module named {name!r} not found')
            if spec.loader is None:
                raise ImportError('spec has no loader')
            assert isinstance(spec.loader, Loader)

            module = importlib.util.module_from_spec(spec)
            loader = importlib.util.LazyLoader(spec.loader)

            sys.modules[spec.name] = module

            try:
                loader.exec_module(module)
            except ImportError:
                del sys.modules[spec.name]
                raise

        return module

    def __mod__(self, other: str) -> None:
        if '.' in other:
            raise ValueError('dot in module name not supported')

        module = self(other)
        spec = module.__spec__
        if spec is None:
            raise RuntimeError('module spec missing')
        caller_frame = sys._getframe(1)
        caller_frame.f_globals[spec.name] = module

lazy_import = _LazyImport()
