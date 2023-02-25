
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.moderation_action_log_entry import ModerationActionLogEntry
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ..stream_SYNC import Stream


def action_log_extractor(x: ModerationActionLogEntry) -> object:
    return x.uuid

def get_action_log_stream_paginator(client: Client, sr: str) -> CursorPaginator[ModerationActionLogEntry]:
    return client.p.moderation.pull_actions(sr).get_paginator()

def make_action_log_stream(paginator: CursorPaginator[ModerationActionLogEntry], past: Optional[Iterable[ModerationActionLogEntry]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[ModerationActionLogEntry]:
    return Stream(paginator, action_log_extractor, past=past, seen=seen)

def create_action_log_stream(client: Client, sr: str) -> IStandardStreamEventSubject[ModerationActionLogEntry]:
    return make_action_log_stream(get_action_log_stream_paginator(client, sr))
