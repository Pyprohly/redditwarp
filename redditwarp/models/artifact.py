
from __future__ import annotations
from typing import Any, Mapping, Protocol, TypeVar
from functools import cached_property

from ..util.data_members_namespace import DataMembersNamespaceMapping
from ..util.attribute_mapping_wrapper import PrettyPrintingAttributeMappingWrapper

class Artifact:
    _TSelf = TypeVar('_TSelf', bound='Artifact')

    def __init__(self: _TSelf, d: Mapping[str, Any]):
        self.d: Mapping[str, Any] = d
        self.a: DataMembersNamespaceMapping[Artifact._TSelf] = DataMembersNamespaceMapping(self)
        self.b: PrettyPrintingAttributeMappingWrapper[Any] = PrettyPrintingAttributeMappingWrapper(d)

class IArtifact(Protocol):
    d: Mapping[str, Any]

    _TSelf = TypeVar('_TSelf')

    @cached_property
    def a(self: _TSelf) -> DataMembersNamespaceMapping[_TSelf]:
        return DataMembersNamespaceMapping(self)

    @cached_property
    def b(self) -> PrettyPrintingAttributeMappingWrapper[Any]:
        return PrettyPrintingAttributeMappingWrapper(self.d)
