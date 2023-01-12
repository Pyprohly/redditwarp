#!/usr/bin/env python

from __future__ import annotations
from typing import Iterator, Generic, TypeVar, Sequence

from dataclasses import dataclass


TValue_co = TypeVar('TValue_co', covariant=True)
TChild_co = TypeVar('TChild_co', covariant=True)

@dataclass(repr=False, eq=False, frozen=True)
class TreeNode(Generic[TValue_co, TChild_co]):
    value: TValue_co
    children: Sequence[TChild_co]

RecursiveTreeNode = TreeNode[TValue_co, 'RecursiveTreeNode[TValue_co]']


T = TypeVar('T')

def depth_first_recursive(node: RecursiveTreeNode[T]) -> Iterator[tuple[int, T]]:
    def traverse(root: RecursiveTreeNode[T], level: int = 0) -> Iterator[tuple[int, T]]:
        value = root.value
        yield (level, value)

        for child in root.children:
            yield from traverse(child, level + 1)

    return traverse(node)

def display_tree_node(tree_node: RecursiveTreeNode[object]) -> None:
    for depth, value in depth_first_recursive(tree_node):
        print(depth*'.', value)


MyTreeNode = RecursiveTreeNode[int]
tree_node = MyTreeNode(
    0,
    [
        MyTreeNode(
            1,
            [
                MyTreeNode(
                    11,
                    [
                        MyTreeNode(
                            111,
                            [],
                        ),
                    ],
                ),
                MyTreeNode(
                    12,
                    [
                        MyTreeNode(
                            121,
                            [
                                MyTreeNode(
                                    1211,
                                    [],
                                ),
                            ],
                        ),
                        MyTreeNode(
                            122,
                            [],
                        ),
                        MyTreeNode(
                            123,
                            [],
                        ),
                    ],
                ),
            ],
        ),
        MyTreeNode(
            2,
            [
                MyTreeNode(
                    21,
                    [
                        MyTreeNode(
                            211,
                            [],
                        ),
                    ],
                ),
            ],
        ),
        MyTreeNode(
            3,
            [],
        ),
    ],
)

display_tree_node(tree_node)
