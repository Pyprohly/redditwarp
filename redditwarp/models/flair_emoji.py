
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, overload, Union

class FlairEmoji:
    def __init__(self, d: Mapping[str, Any], name: str):
        self.name = name
        self.d = d
        full_id36: str = d['created_by']
        _, _, id36 = full_id36.partition('_')
        self.creator_id36: str = id36
        self.creator_id = int(id36, 36)
        self.image_url: str = d['url']
        self.post_enabled: bool = d['post_flair_allowed']
        self.user_enabled: bool = d['user_flair_allowed']
        self.mod_only: bool = d['mod_flair_only']


class SubredditFlairEmojiInventory(Sequence[FlairEmoji]):
    def __init__(self,
            subreddit_emojis: Sequence[FlairEmoji],
            reddit_emojis: Sequence[FlairEmoji],
            subreddit_id36: str):
        self.subreddit_emojis = subreddit_emojis
        self.reddit_emojis = reddit_emojis
        self.all_emojis: Sequence[FlairEmoji] = list(self.subreddit_emojis) + list(self.reddit_emojis)
        self.subreddit_id36 = subreddit_id36
        self.subreddit_id = int(subreddit_id36, 36)

    def __len__(self) -> int:
        return len(self.subreddit_emojis)

    def __contains__(self, item: object) -> bool:
        return item in self.subreddit_emojis

    def __iter__(self) -> Iterator[FlairEmoji]:
        return iter(self.subreddit_emojis)

    @overload
    def __getitem__(self, index: int) -> FlairEmoji: pass
    @overload
    def __getitem__(self, index: slice) -> Sequence[FlairEmoji]: pass
    def __getitem__(self, index: Union[int, slice]) -> Union[FlairEmoji, Sequence[FlairEmoji]]:
        return self.subreddit_emojis[index]
