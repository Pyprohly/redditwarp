
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, MutableSequence, Callable, Generic, TypeVar, Protocol, Awaitable, Generator, Optional, Iterator, AsyncIterator
if TYPE_CHECKING:
    from asyncio import Future
    from ..pagination.async_paginator import CursorAsyncPaginator

import asyncio
import random
import time

from ..pagination.async_paginator import Resettable
from ..util.ordered_set import BoundedSet
from ..util.event_dispatcher import EventDispatcher


TEvent_contra = TypeVar('TEvent_contra', contravariant=True)
TEvent = TypeVar('TEvent')

class StreamEventHandlerProtocol(Protocol[TEvent_contra]):
    async def __call__(self, event: TEvent_contra, /) -> None:
        ...

class StreamEventDispatcher(EventDispatcher[StreamEventHandlerProtocol[TEvent]], Generic[TEvent]):
    async def __call__(self, event: TEvent) -> None:
        for handler in self:
            await handler(event)


TOutput = TypeVar('TOutput')

class IStandardStreamEventSubject(Awaitable[None], AsyncIterator[float], Generic[TOutput]):
    output: StreamEventDispatcher[TOutput]
    error: StreamEventDispatcher[Exception]

    def __aiter__(self) -> AsyncIterator[float]:
        raise NotImplementedError

    async def __anext__(self) -> float:
        raise NotImplementedError

    def __await__(self) -> Generator[Optional[Future[None]], None, None]:
        raise NotImplementedError



class Stream(IStandardStreamEventSubject[TOutput]):
    _BASE_POLL_INTERVAL: float = 5.0
    _MAX_POLL_INTERVAL: float = 42.0
    _BACKOFF_FACTOR: float =  2.0
    _JITTER_FACTOR: float = 0.4

    _MEMORY: int = 2000
    _TARGET_LIMIT_MULTIPLIER: float = 1.2

    _BACKTRACK_DEPTH: int = 300

    def __init__(self,
        paginator: CursorAsyncPaginator[TOutput],
        extractor: Callable[[TOutput], object],
        *,
        max_limit: int = 100,
    ) -> None:
        if not isinstance(paginator, Resettable):
            raise ValueError('paginator must be Resettable')
        self._paginator: CursorAsyncPaginator[TOutput] = paginator
        self._paginator__resettable: Resettable = paginator
        self._extractor: Callable[[TOutput], object] = extractor
        self._max_limit: int = max_limit

        self._agen: AsyncIterator[float] = self.__routine()

        self.output: StreamEventDispatcher[TOutput] = StreamEventDispatcher()
        self.error: StreamEventDispatcher[Exception] = StreamEventDispatcher()

    def __aiter__(self) -> AsyncIterator[float]:
        return self

    async def __anext__(self) -> float:
        return await self._agen.__anext__()

    def __await__(self) -> Generator[Optional[Future[None]], None, None]:
        async def _coro_func() -> None:
            async for t in self:
                await asyncio.sleep(t)
        return _coro_func().__await__()

    @staticmethod
    def _intermit(duration: float) -> Iterator[float]:
        point = time.monotonic() + duration
        yield duration
        while (n := point - time.monotonic()) > 0:
            yield n

    async def __routine(self) -> AsyncIterator[float]:
        paginator = self._paginator
        paginator__resettable = self._paginator__resettable
        extractor = self._extractor
        max_limit = self._max_limit

        seen: BoundedSet[object] = BoundedSet((), self._MEMORY)
        delay: float = self._BASE_POLL_INTERVAL

        paginator.limit = max_limit

        retrieved: Sequence[TOutput] = ()
        while True:
            try:
                retrieved = await paginator.fetch()
            except Exception as error:
                await self.emit_error(error)
                if delay < self._MAX_POLL_INTERVAL:
                    delay = min(self._BACKOFF_FACTOR * delay, self._MAX_POLL_INTERVAL)
                for v in self._intermit(random.uniform(
                        delay * (1 - self._JITTER_FACTOR),
                        delay * (1 + self._JITTER_FACTOR))):
                    yield v
                continue
            break

        delay = self._BASE_POLL_INTERVAL

        paginator__resettable.reset()

        for obj in retrieved:
            seen.add(extractor(obj))

        yield 0

        tuna_limit: float = max_limit
        backtrack_count: int = 0

        while True:
            effective_limit = round(tuna_limit)
            paginator.limit = effective_limit

            retrieved = ()
            fetch_successful: bool = True
            try:
                retrieved = await paginator.fetch()
            except Exception as error:
                fetch_successful = False
                await self.emit_error(error)

            selection: MutableSequence[TOutput] = []
            for obj in retrieved:
                identity = self._extractor(obj)
                if identity not in seen:
                    seen.add(identity)
                    selection.append(obj)

            for obj in selection:
                await self.emit_output(obj)

            backtrack_count += len(selection)

            if (len(selection) < effective_limit) or (backtrack_count > self._BACKTRACK_DEPTH):
                paginator__resettable.reset()
                backtrack_count = 0

            if fetch_successful:
                tuna = tuna_limit
                if not selection:
                    tuna = max(tuna/2, 1)
                elif len(selection) >= effective_limit:
                    tuna = min(2*tuna, max_limit)
                else:
                    tuna = min((self._TARGET_LIMIT_MULTIPLIER * len(selection)), max_limit)
                tuna_limit = tuna

            if fetch_successful:
                delay = self._BASE_POLL_INTERVAL
            else:
                if delay < self._MAX_POLL_INTERVAL:
                    delay = min(self._BACKOFF_FACTOR * delay, self._MAX_POLL_INTERVAL)

            t = 1.
            if not paginator.get_cursor():
                t = random.uniform(
                        delay * (1 - self._JITTER_FACTOR),
                        delay * (1 + self._JITTER_FACTOR))
            for v in self._intermit(t):
                yield v

    async def emit_output(self, output: TOutput) -> None:
        await self.output(output)

    async def emit_error(self, error: Exception) -> None:
        await self.error(error)
