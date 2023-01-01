
from __future__ import annotations
from typing import Sequence, overload, Iterator, Union, Mapping, Any, Optional

from datetime import datetime
from dataclasses import dataclass

from .artifact import IArtifact
from .subreddit import Subreddit

@dataclass(repr=False, eq=False)
class Draft(IArtifact):
    @dataclass(repr=False, eq=False)
    class FlairInfo:
        uuid: str = ''
        type: str = ''
        text_override: str = ''
        bg_color: str = ''
        fg_light_or_dark: str = ''

    d: Mapping[str, Any]
    uuid: str
    created_at: datetime
    modified_at: datetime
    public: bool
    subreddit_id: Optional[int]
    title: str
    reply_notifications: bool
    spoiler: bool
    nsfw: bool
    original_content: bool
    flair: Optional[FlairInfo]

@dataclass(repr=False, eq=False)
class MarkdownDraft(Draft):
    body: str

@dataclass(repr=False, eq=False)
class RichTextDraft(Draft):
    pass


class DraftList(Sequence[Draft]):
    @property
    def subreddits(self) -> Sequence[Subreddit]:
        return self.__subreddits

    def __init__(self,
        drafts: Sequence[Draft],
        subreddits: Sequence[Subreddit],
    ) -> None:
        self.drafts: Sequence[Draft] = drafts
        self.__subreddits: Sequence[Subreddit] = subreddits

    def __len__(self) -> int:
        return len(self.drafts)

    def __contains__(self, item: object) -> bool:
        return item in self.drafts

    def __iter__(self) -> Iterator[Draft]:
        return iter(self.drafts)

    @overload
    def __getitem__(self, index: int) -> Draft: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Draft]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Draft, Sequence[Draft]]:
        return self.drafts[index]
