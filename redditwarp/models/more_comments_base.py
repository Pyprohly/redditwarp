
from __future__ import annotations
from typing import Optional, Mapping, Any

class MoreCommentsBase:
    def __init__(self,
        submission_id36: str,
        comment_id36: str,
        sort: Optional[str],
        *,
        d: Mapping[str, Any],
    ):
        self.submission_id36 = submission_id36
        self.comment_id36 = comment_id36
        self.sort = sort
        self.d = d
