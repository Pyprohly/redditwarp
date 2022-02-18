
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence, TypeVar, overload, Iterator, Union

from datetime import datetime, timezone

from .artifact import Artifact

class BaseSubmissionCollectionDetails(Artifact):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.uuid: str = d['collection_id']

        full_id36: str = d['subreddit_id']
        _, _, id36 = full_id36.partition('_')
        self.subreddit_id36: str = id36
        self.subreddit_id: int = int(id36, 36)

        full_id36 = d['author_id']
        _, _, id36 = full_id36.partition('_')
        self.author_id36: str = id36
        self.author_id: int = int(id36, 36)

        self.author_name: str = d['author_name']
        self.title: str = d['title']
        self.description: str = d['description']

        self.created_ts: float = d['created_at_utc']
        self.created_at: datetime = datetime.fromtimestamp(self.created_ts, timezone.utc)
        self.last_post_added_ut: float = d['last_update_utc']
        self.last_post_added_at: datetime = datetime.fromtimestamp(self.last_post_added_ut, timezone.utc)

        self.display_layout: Optional[str] = d['display_layout']
        self.layout: str = 'TIMELINE'
        if self.display_layout is not None:
            self.layout = self.display_layout

        submission_full_id36s: Sequence[str] = d['link_ids']
        self.submission_id36s: Sequence[str] = [s[3:] for s in submission_full_id36s]
        self.submission_ids: Sequence[int] = [int(s, 36) for s in self.submission_id36s]

class BaseSubmissionCollection(BaseSubmissionCollectionDetails):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)

TSubmission = TypeVar('TSubmission')

class GBaseSubmissionCollection(BaseSubmissionCollection, Sequence[TSubmission]):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        children_data = d['sorted_links']['data']['children']
        subms = [self._load_submission(i['data']) for i in children_data]
        self.submissions: Sequence[TSubmission] = subms

    def __len__(self) -> int:
        return len(self.submissions)

    def __contains__(self, item: object) -> bool:
        return item in self.submissions

    def __iter__(self) -> Iterator[TSubmission]:
        return iter(self.submissions)

    @overload
    def __getitem__(self, index: int) -> TSubmission: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[TSubmission]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[TSubmission, Sequence[TSubmission]]:
        return self.submissions[index]

    def _load_submission(self, m: Mapping[str, Any]) -> TSubmission:
        raise NotImplementedError
