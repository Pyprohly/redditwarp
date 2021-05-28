
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, List, overload, Union

class FlairEmoji:
    def __init__(self, d: Mapping[str, Any], name: str):
        self.name = name
        self.d = d
        _full_id36: str = d['created_by']
        _, _, id36 = _full_id36.partition('_')
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
        self._combined = list(self.subreddit_emojis) + list(self.reddit_emojis)
        self.subreddit_id36 = subreddit_id36
        self.subreddit_id = int(subreddit_id36, 36)

    def __len__(self) -> int:
        return len(self._combined)

    def __contains__(self, item: object) -> bool:
        return item in self._combined

    def __iter__(self) -> Iterator[FlairEmoji]:
        return iter(self._combined)

    @overload
    def __getitem__(self, index: int) -> FlairEmoji: pass
    @overload
    def __getitem__(self, index: slice) -> List[FlairEmoji]: pass
    def __getitem__(self, index: Union[int, slice]) -> Union[FlairEmoji, List[FlairEmoji]]:
        return self._combined[index]