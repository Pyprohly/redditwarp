
from __future__ import annotations
from typing import Any, Mapping

from ..models.subreddit_rules import SubredditRules

def load_subreddit_rules(d: Mapping[str, Any]) -> SubredditRules:
    return SubredditRules(d)
