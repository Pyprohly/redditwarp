"""General tree node data structures."""

from __future__ import annotations
from typing import TypeVar, Generic, Optional, Sequence

from dataclasses import dataclass

T = TypeVar('T')
TChild = TypeVar('TChild')

@dataclass(repr=False, eq=False)
class GeneralTreeNode(Generic[T, TChild]):
    value: T
    children: Sequence[TChild]

@dataclass(repr=False, eq=False)
class BinaryTreeNode(Generic[T, TChild]):
    value: T
    left: Optional[TChild]
    right: Optional[TChild]
