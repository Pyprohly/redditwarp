
from __future__ import annotations
from typing import Mapping, Any, Iterator

from dataclasses import dataclass

from .upload_lease import UploadLease as FlairEmojiUploadLease  # noqa: F401


@dataclass(repr=False, eq=False)
class FlairEmoji:
    d: Mapping[str, Any]
    name: str
    image_url: str
    creator_idn: int
    creator_id: int
    creator_id36: str
    post_enabled: bool
    user_enabled: bool
    mod_only: bool


class SubredditFlairEmojis(Mapping[str, FlairEmoji]):
    def __init__(self,
        *,
        subreddit_emojis: Mapping[str, FlairEmoji],
        reddit_emojis: Mapping[str, FlairEmoji],
        all_emojis: Mapping[str, FlairEmoji],
        subreddit_id36: str,
    ) -> None:
        self.subreddit_emojis: Mapping[str, FlairEmoji] = subreddit_emojis
        ("")
        self.reddit_emojis: Mapping[str, FlairEmoji] = reddit_emojis
        ("")
        self.all_emojis: Mapping[str, FlairEmoji] = all_emojis
        ("")
        self.subreddit_id36: str = subreddit_id36
        ("")
        self.subreddit_idn: int = int(subreddit_id36, 36)
        ("")
        self.subreddit_id: int = self.subreddit_idn
        ("")

    def __contains__(self, item: object) -> bool:
        return item in self.all_emojis

    def __iter__(self) -> Iterator[str]:
        return iter(self.all_emojis)

    def __len__(self) -> int:
        return len(self.all_emojis)

    def __getitem__(self, key: str) -> FlairEmoji:
        return self.all_emojis[key]
