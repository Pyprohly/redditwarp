
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Sequence

from dataclasses import dataclass

T = TypeVar('T')
TChild = TypeVar('TChild')

@dataclass(repr=False, eq=False)
class Node(Generic[T]):
    value: T

@dataclass(repr=False, eq=False)
class TreeNode(Node[T], Generic[T, TChild]):
    pass

@dataclass(repr=False, eq=False)
class GeneralTreeNode(TreeNode[T, TChild]):
    children: Sequence[TChild]

@dataclass(repr=False, eq=False)
class BinaryTreeNode(TreeNode[T, TChild]):
    left: Optional[TChild]
    right: Optional[TChild]
