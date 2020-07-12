
from typing import TypeVar, Iterable, AsyncIterable, AsyncIterator

import pytest  # type: ignore[import]

from redditwarp.iterators.unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

T = TypeVar('T')

async def A(iterable: Iterable[T]) -> AsyncIterable[T]:
    for i in iterable:
        yield i

@pytest.mark.asyncio
async def test_simple_iteration() -> None:
    it: AsyncIterable[AsyncIterable[int]] = A([A([62, 43, 13]), A([12, 38])])
    uci = UnfalteringChainingAsyncIterator(it)
    assert [i async for i in uci] == [62, 43, 13, 12, 38]
    it = A(())
    assert [i async for i in UnfalteringChainingAsyncIterator(it)] == []

@pytest.mark.asyncio
async def test_current_iter() -> None:
    it = A([A([62, 43, 13]), A([12, 38])])
    uci = UnfalteringChainingAsyncIterator(it)
    assert await uci.__anext__() == 62
    assert [i async for i in uci.current_iter] == [43, 13]
    assert await uci.__anext__() == 12
    assert [i async for i in uci.current_iter] == [38]
    uci.current_iter = A((77,)).__aiter__()
    assert [i async for i in uci.current_iter] == [77]

@pytest.mark.asyncio
async def test_exception_during_iteration() -> None:
    class throw_on_first_call_then_return:
        def __init__(self) -> None:
            self.call_count = 0
        async def __aiter__(self) -> AsyncIterator[int]:
            self.call_count += 1
            if self.call_count == 1:
                raise RuntimeError
            for i in (-2, -3):
                yield i

    j = throw_on_first_call_then_return()
    it: AsyncIterable[AsyncIterable[int]] = A([
        A((0, 1)),
        j,
        A((4, 5)),
    ])
    uci = UnfalteringChainingAsyncIterator(it)
    assert await uci.__anext__() == 0
    assert await uci.__anext__() == 1
    try:
        await uci.__anext__()
    except RuntimeError:
        pass
    assert await uci.__anext__() == 4
    assert await uci.__anext__() == 5
