
from __future__ import annotations
from typing import TypeVar, Generic, Sequence

from dataclasses import dataclass

E = TypeVar('E')

@dataclass
class Node(Generic[E]):
    value: E

@dataclass
class GenericTreeNode(Node[E]):
    children: Sequence[GenericTreeNode[E]]
