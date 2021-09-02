
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, overload, Union

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class FlairEmoji:
    d: Mapping[str, Any]
    name: str
    creator_id36: str
    creator_id: int
    image_url: str
    post_enabled: bool
    user_enabled: bool
    mod_only: bool


class SubredditFlairEmojis(Sequence[FlairEmoji]):
    def __init__(self,
            subreddit_emojis: Sequence[FlairEmoji],
            reddit_emojis: Sequence[FlairEmoji],
            subreddit_id36: str):
        self.subreddit_emojis = subreddit_emojis
        self.reddit_emojis = reddit_emojis
        #self.all_emojis: Sequence[FlairEmoji] = list(self.subreddit_emojis) + list(self.reddit_emojis)
        self.subreddit_id36 = subreddit_id36
        self.subreddit_id = int(subreddit_id36, 36)

    def __len__(self) -> int:
        return len(self.subreddit_emojis)

    def __contains__(self, item: object) -> bool:
        return item in self.subreddit_emojis

    def __iter__(self) -> Iterator[FlairEmoji]:
        return iter(self.subreddit_emojis)

    @overload
    def __getitem__(self, index: int) -> FlairEmoji: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[FlairEmoji]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[FlairEmoji, Sequence[FlairEmoji]]:
        return self.subreddit_emojis[index]
