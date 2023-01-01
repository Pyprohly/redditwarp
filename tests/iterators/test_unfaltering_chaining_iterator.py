
from typing import Iterable, Iterator

from redditwarp.iterators.unfaltering_chaining_iterator import UnfalteringChainingIterator

def test_simple_iteration() -> None:
    it = [[62, 43, 13], [12, 38]]
    uci = UnfalteringChainingIterator(it)
    assert list(uci) == [62, 43, 13, 12, 38]
    assert list(UnfalteringChainingIterator(())) == []

def test_empty_link() -> None:
    it: Iterable[Iterable[int]]
    it = [[62, 43, 13], [], [12, 38]]
    uci = UnfalteringChainingIterator(it)
    assert list(uci) == [62, 43, 13, 12, 38]
    assert list(UnfalteringChainingIterator(())) == []

def test_current_iter() -> None:
    it = [[62, 43, 13], [12, 38]]
    uci = UnfalteringChainingIterator(it)
    assert next(uci) == 62
    assert list(uci.current_iterator) == [43, 13]
    assert next(uci) == 12
    assert list(uci.current_iterator) == [38]
    uci.current_iterator = iter((77,))
    assert list(uci.current_iterator) == [77]

def test_exception_during_iteration() -> None:
    class throw_on_first_call_then_return:
        def __init__(self) -> None:
            self.call_count = 0
        def __iter__(self) -> Iterator[int]:
            self.call_count += 1
            if self.call_count == 1:
                raise RuntimeError
            yield from (-2, -3)

    j = throw_on_first_call_then_return()
    it: Iterable[Iterable[int]] = [
        (0, 1),
        j,
        (4, 5),
    ]
    uci = UnfalteringChainingIterator(it)
    assert next(uci) == 0
    assert next(uci) == 1
    try:
        next(uci)
    except RuntimeError:
        pass
    assert next(uci) == 4
    assert next(uci) == 5
