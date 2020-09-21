
from __future__ import annotations
from typing import TypeVar, Generic, Sequence

from dataclasses import dataclass

E = TypeVar('E')

@dataclass
class Node(Generic[E]):
    value: E

@dataclass
class GeneralTreeNode(Node[E]):
    children: Sequence[GeneralTreeNode[E]]
