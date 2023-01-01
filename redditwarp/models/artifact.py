
from __future__ import annotations
from typing import Any, Mapping
from functools import cached_property

from ..util.data_members_namespace import DataMembersNamespaceMapping
from ..util.attribute_mapping_proxy import DictAndListRecursiveAttributeMappingProxy

class Artifact:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.a: DataMembersNamespaceMapping = DataMembersNamespaceMapping(self)
        self.b: DictAndListRecursiveAttributeMappingProxy[Any] = DictAndListRecursiveAttributeMappingProxy(d)

class IArtifact:
    d: Mapping[str, Any]

    @cached_property
    def a(self) -> DataMembersNamespaceMapping:
        return DataMembersNamespaceMapping(self)

    @cached_property
    def b(self) -> DictAndListRecursiveAttributeMappingProxy[Any]:
        return DictAndListRecursiveAttributeMappingProxy(self.d)
