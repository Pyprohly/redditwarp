"""Provides functions that makes functions more decorator-friendly."""

from __future__ import annotations
from typing import TypeVar, Callable

T = TypeVar('T')

def passthru(func: Callable[[T], None]) -> Callable[[T], T]:
    """Make a function that takes an argument and returns `None` return the argument that was given to it."""
    def inner(arg: T) -> T:
        func(arg)
        return arg
    return inner

def passover(func: Callable[[T], object]) -> Callable[[T], T]:
    """Same as `passthru()` but accept any function returning any type instead of just `None`."""
    def inner(arg: T) -> T:
        func(arg)
        return arg
    return inner
