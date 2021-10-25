
from __future__ import annotations
from typing import Mapping, Any

from functools import cached_property

class BaseMoreComments:
    def __init__(self,
        submission_id36: str,
        comment_id36: str,
        sort: str,
        *,
        d: Mapping[str, Any],
    ):
        self.submission_id36: str = submission_id36
        self.comment_id36: str = comment_id36
        self.sort: str = sort
        self.d: Mapping[str, Any] = d

    @cached_property
    def submission_id(self) -> int:
        return int(self.submission_id36, 36)

    @cached_property
    def comment_id(self) -> int:
        return int(self.comment_id36, 36)
