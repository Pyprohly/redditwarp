
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Iterable, Optional, Tuple
if TYPE_CHECKING:
    from ...pagination.async_paginator import CursorAsyncPaginator

from ...models.modmail_ASYNC import ConversationInfo, Message

from .stream_ASYNC import CommonStreamBase

class ModmailStream(CommonStreamBase[Tuple[ConversationInfo, Message]]):
    def __init__(self,
        paginator: CursorAsyncPaginator[tuple[ConversationInfo, Message]],
        *,
        max_limit: int = 100,
        past: Optional[Iterable[tuple[ConversationInfo, Message]]] = None,
        memory: int = 2000,
    ) -> None:
        super().__init__(
            paginator,
            max_limit=max_limit,
            past=past,
        )

        def checkin_func_fn(*,
            memory: int,
        ) -> Callable[[tuple[ConversationInfo, Message]], bool]:
            def extractor(x: tuple[ConversationInfo, Message]) -> tuple[object, object]:
                return (x[0].id, x[1].id)

            seen: dict[object, object] = {}

            def fn(obj: tuple[ConversationInfo, Message]) -> bool:
                k, v = extractor(obj)
                if seen.get(k) == v:
                    return False
                if len(seen) >= memory:
                    del seen[next(iter(seen))]
                seen.pop(k, None)
                seen[k] = v
                return True

            return fn

        self._checkin_func = checkin_func_fn(memory=memory)

    def _checkin(self, obj: tuple[ConversationInfo, Message]) -> bool:
        return self._checkin_func(obj)
