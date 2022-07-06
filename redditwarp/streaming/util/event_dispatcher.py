
from __future__ import annotations
from typing import TypeVar, Iterator#, Optional, overload, Callable, Union
from collections.abc import Collection

T = TypeVar('T')

class EventDispatcher(Collection[T]):
    def __init__(self) -> None:
        self._handlers: set[T] = set()

    def __len__(self) -> int:
        return len(self._handlers)

    def __contains__(self, item: object) -> bool:
        return item in self._handlers

    def __iter__(self) -> Iterator[T]:
        return iter(self._handlers)

    def attach(self, handler: T) -> None:
        self._handlers.add(handler)

    def detach(self, handler: T) -> None:
        self._handlers.discard(handler)

    '''
    @overload
    def attach_handler(self) -> Callable[[T], T]: ...
    @overload
    def attach_handler(self, handler: T) -> T: ...
    def attach_handler(self, handler: Optional[T] = None) -> Union[Callable[[T], T], T]:
        """Same as `self.attach` but returns the given argument."""
        if handler is None:
            return self.attach_handler
        self.attach(handler)
        return handler

    attach_passthru = attach_handler
    '''




from typing import Protocol

def _main() -> None:
    class Example:
        pass

    class ExampleHandlerProtocol(Protocol):
        def __call__(self, example: Example, /) -> None:
            ...

    class ExampleEventDispatcher(EventDispatcher[ExampleHandlerProtocol]):
        def __call__(self, example: Example) -> None:
            for handler in self:
                handler(example)

    example_event = ExampleEventDispatcher()

    def handler1(example: Example) -> None:
        print('Got:', example)

    example_event.attach(handler1)

    @example_event.attach
    def handler2(obj: object) -> None:
        print('Got:', obj)

    example_event(Example())

if __name__ == '__main__':
    _main()
