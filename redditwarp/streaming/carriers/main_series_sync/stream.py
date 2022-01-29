
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, MutableSequence, Callable, Generic, TypeVar, Iterator, Protocol
if TYPE_CHECKING:
    from ....pagination.paginator import CursorPaginator

import random

from ....pagination.paginator import Resettable
from ....util.ordered_set import BoundedSet
from ...util.event_dispatcher import EventDispatcher


TEvent_contra = TypeVar('TEvent_contra', contravariant=True)
TEvent = TypeVar('TEvent')

class IStreamEventHandler(Protocol[TEvent_contra]):
    def __call__(self, event: TEvent_contra, /) -> None:
        ...

class StreamEventDispatcher(EventDispatcher[IStreamEventHandler[TEvent]], Generic[TEvent]):
    def __call__(self, event: TEvent) -> None:
        for handler in self:
            handler(event)


TOutput = TypeVar('TOutput')

class IStandardStreamEventSubject(Iterator[float], Protocol[TOutput]):
    output: StreamEventDispatcher[TOutput]
    error: StreamEventDispatcher[Exception]

    def __iter__(self) -> Iterator[float]: ...
    def __next__(self) -> float: ...


class Stream(IStandardStreamEventSubject[TOutput]):
    _BASE_POLL_INTERVAL: float = 5.0
    _MAX_POLL_INTERVAL: float = 50.0
    _BACKOFF_FACTOR: float =  2.0
    _JITTER_FACTOR: float = 0.4

    _MEMORY: int = 2000
    _TARGET_LIMIT_MULTIPLIER: float = 1.2

    _BACKTRACK_DEPTH: int = 300

    def __init__(self,
        paginator: CursorPaginator[TOutput],
        extractor: Callable[[TOutput], object],
        *,
        max_limit: int = 100,
    ) -> None:
        if not isinstance(paginator, Resettable):
            raise ValueError('paginator must be Resettable')
        self._paginator: CursorPaginator[TOutput] = paginator
        self._paginator__resettable: Resettable = paginator
        self._extractor: Callable[[TOutput], object] = extractor
        self._max_limit: int = max_limit

        self._gen: Iterator[float] = self.__routine()

        self.output: StreamEventDispatcher[TOutput] = StreamEventDispatcher()
        self.error: StreamEventDispatcher[Exception] = StreamEventDispatcher()

    def __iter__(self) -> Iterator[float]:
        return self

    def __next__(self) -> float:
        return next(self._gen)

    def __routine(self) -> Iterator[float]:
        paginator = self._paginator
        assert isinstance(paginator, Resettable)
        paginator__resettable = paginator
        extractor = self._extractor
        max_limit = self._max_limit

        seen: BoundedSet[object] = BoundedSet((), self._MEMORY)
        delay: float = self._BASE_POLL_INTERVAL

        paginator.limit = max_limit

        retrieved: Sequence[TOutput] = ()
        while not retrieved:
            try:
                retrieved = paginator.fetch()
            except Exception as error:
                self.emit_error(error)
                if delay < self._MAX_POLL_INTERVAL:
                    delay = min(self._BACKOFF_FACTOR * delay, self._MAX_POLL_INTERVAL)
                yield random.uniform(
                    delay * (1 - self._JITTER_FACTOR),
                    delay * (1 + self._JITTER_FACTOR))

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
                retrieved = paginator.fetch()
            except Exception as error:
                fetch_successful = False
                self.emit_error(error)

            selection: MutableSequence[TOutput] = []
            for obj in retrieved:
                identity = self._extractor(obj)
                if identity not in seen:
                    seen.add(identity)
                    selection.append(obj)

            for obj in selection:
                self.emit_output(obj)

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

            if paginator.get_cursor():
                yield 1
            else:
                yield random.uniform(
                        delay * (1 - self._JITTER_FACTOR),
                        delay * (1 + self._JITTER_FACTOR))

    def emit_output(self, output: TOutput) -> None:
        self.output(output)

    def emit_error(self, error: Exception) -> None:
        self.error(error)
