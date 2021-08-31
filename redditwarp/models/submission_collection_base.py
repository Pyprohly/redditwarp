
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence, TypeVar, overload, Iterator, Union

from .artifact import Artifact

from datetime import datetime, timezone

class SubmissionCollectionDetailsMixinBase(Artifact):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.uuid: str = d['collection_id']

        full_id36: str = d['subreddit_id']
        _, _, id36 = full_id36.partition('_')
        self.subreddit_id36 = id36
        self.subreddit_id = int(id36, 36)

        full_id36 = d['author_id']
        _, _, id36 = full_id36.partition('_')
        self.author_id36 = id36
        self.author_id = int(id36, 36)

        self.author_name: str = d['author_name']
        self.title: str = d['title']
        self.description: str = d['description']

        self.created_ut: float = d['created_at_utc']
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.last_post_added_ut: float = d['last_update_utc']
        self.last_post_added_at = datetime.fromtimestamp(self.last_post_added_ut, timezone.utc)

        self.display_layout: Optional[str] = d['display_layout']
        self.layout = 'TIMELINE'
        if self.display_layout is not None:
            self.layout = self.display_layout

        submission_full_id36s: Sequence[str] = d['link_ids']
        self.submission_id36s: Sequence[str] = [s[3:] for s in submission_full_id36s]
        self.submission_ids: Sequence[int] = [int(s, 36) for s in self.submission_id36s]

T = TypeVar('T')

class GenericSubmissionCollectionMixinBase(SubmissionCollectionDetailsMixinBase, Sequence[T]):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.submissions: Sequence[T] = ()

    def __len__(self) -> int:
        return len(self.submissions)

    def __contains__(self, item: object) -> bool:
        return item in self.submissions

    def __iter__(self) -> Iterator[T]:
        return iter(self.submissions)

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[T, Sequence[T]]:
        return self.submissions[index]

class SubmissionCollectionMixinBase(SubmissionCollectionDetailsMixinBase):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
