"""General tree node data structure."""

from __future__ import annotations
from typing import TypeVar, Generic, Sequence

from dataclasses import dataclass


TValue_co = TypeVar('TValue_co', covariant=True)
TChild_co = TypeVar('TChild_co', covariant=True)

@dataclass(repr=False, eq=False, frozen=True)
class TreeNode(Generic[TValue_co, TChild_co]):
    value: TValue_co
    children: Sequence[TChild_co]

RecursiveTreeNode = TreeNode[TValue_co, 'RecursiveTreeNode[TValue_co]']
