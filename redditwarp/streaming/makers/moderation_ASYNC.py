
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.moderation_action_log_entry import ModerationActionLogEntry
    from ..impls.stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ..impls.stream_ASYNC import SimpleImprintExtractorStream


def get_action_log_stream_paginator(client: Client, sr: str) -> CursorAsyncPaginator[ModerationActionLogEntry]:
    return client.p.moderation.pull_actions(sr).get_paginator()

def make_action_log_stream(paginator: CursorAsyncPaginator[ModerationActionLogEntry], past: Optional[Iterable[ModerationActionLogEntry]] = None) -> IStandardStreamEventSubject[ModerationActionLogEntry]:
    def action_log_extractor(x: ModerationActionLogEntry) -> object:
        return x.uuid
    return SimpleImprintExtractorStream(paginator, action_log_extractor, past=past)

def create_action_log_stream(client: Client, sr: str) -> IStandardStreamEventSubject[ModerationActionLogEntry]:
    return make_action_log_stream(get_action_log_stream_paginator(client, sr))
