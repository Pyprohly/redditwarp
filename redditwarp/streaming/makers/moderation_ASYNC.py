
from __future__ import annotations
from typing import TYPE_CHECKING, overload, cast
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.moderation_action_log_entry import ModerationActionLogEntry
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ..stream_ASYNC import Stream


def get_action_log_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[ModerationActionLogEntry]:
    return client.p.moderation.pull_actions(sr).get_paginator()

@overload
def make_action_log_stream(paginator: CursorAsyncPaginator[ModerationActionLogEntry], /) -> IStandardStreamEventSubject[ModerationActionLogEntry]: ...
@overload
def make_action_log_stream(client: Client, sr: str, /) -> IStandardStreamEventSubject[ModerationActionLogEntry]: ...
def make_action_log_stream(*args: object) -> IStandardStreamEventSubject[ModerationActionLogEntry]:
    paginator: CursorAsyncPaginator[ModerationActionLogEntry]
    if len(args) == 1:
        args = cast("tuple[CursorAsyncPaginator[ModerationActionLogEntry]]", args)
        paginator, = args
    else:
        args = cast("tuple[Client, str]", args)
        client, sr = args
        paginator = client.p.moderation.pull_actions(sr).get_paginator()
    return Stream(paginator, lambda x: x.uuid)
