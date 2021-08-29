
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Sequence

T = TypeVar('T')
TChild = TypeVar('TChild')

class Node(Generic[T]):
    def __init__(self, value: T):
        self.value = value

class TreeNode(Node[T], Generic[T, TChild]):
    pass

class GeneralTreeNode(TreeNode[T, TChild]):
    def __init__(self,
        value: T,
        children: Sequence[TChild],
    ):
        super().__init__(value)
        self.children = children

class BinaryTreeNode(TreeNode[T, TChild]):
    def __init__(self,
        value: T,
        left: Optional[TChild],
        right: Optional[TChild],
    ):
        super().__init__(value)
        self.left = left
        self.right = right
