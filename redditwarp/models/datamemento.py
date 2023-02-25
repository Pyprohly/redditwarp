
from __future__ import annotations
from typing import Any, Mapping

from functools import cached_property

from ..util.attribute_mapping_proxy import DictAndListRecursiveAttributeMappingProxy


D = Mapping[str, Any]
B = DictAndListRecursiveAttributeMappingProxy[Any]


class DatamementoPropertiesMixin:
    d: D

    @cached_property
    def b(self) -> B:
        return DictAndListRecursiveAttributeMappingProxy(self.d)


class DatamementoBase:
    def __init__(self, d: D) -> None:
        self.d: D = d
        self.b: B = DictAndListRecursiveAttributeMappingProxy(d)


class DatamementoDataclassesMixin:
    d: D
    b: B

    def __post_init__(self) -> None:
        object.__setattr__(self, 'b', DictAndListRecursiveAttributeMappingProxy(self.d))
