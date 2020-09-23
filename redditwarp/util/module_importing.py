
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec

import sys
import importlib.util
from importlib.abc import Loader

def load_module_from_spec(spec: ModuleSpec) -> ModuleType:
    if spec.loader is None:
        raise RuntimeError('spec has no loader')
    assert isinstance(spec.loader, Loader)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def lazy_import(name: str) -> ModuleType:
    try:
        module = sys.modules[name]
    except KeyError:
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ImportError(f'module named {name!r} not found')
        if spec.loader is None:
            raise RuntimeError('spec has no loader')
        assert isinstance(spec.loader, Loader)

        module = importlib.util.module_from_spec(spec)
        loader = importlib.util.LazyLoader(spec.loader)
        sys.modules[name] = module
        try:
            loader.exec_module(module)
        except ImportError:
            del sys.modules[name]
            raise

    globals()[name] = module
    return module
