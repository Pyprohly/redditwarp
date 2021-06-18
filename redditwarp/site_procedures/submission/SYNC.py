
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission as SubmissionModel

from ...models.load.submission_SYNC import load_submission
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from .fetch_SYNC import Fetch
from .get_SYNC import Get

class Submission:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch = Fetch(self, client)
        self.get = Get(client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingIterator[int, SubmissionModel]:
        def mass_fetch(ids: Sequence[int]) -> Sequence[SubmissionModel]:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_submission(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(
                CallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    def edit_text_post_body(self, submission_id: int, text: str) -> SubmissionModel:
        data = {
            'thing_id': 't3_' + to_base36(submission_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/editusertext', data=data)
        return load_submission(result, self._client)

    def delete(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/del', data=data)

    def lock(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/lock', data=data)

    def unlock(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unlock', data=data)

    def vote(self, submission_id: int, direction: int) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'dir': str(direction),
        }
        self._client.request('POST', '/api/vote', data=data)

    def save(self, submission_id: int, category: Optional[str] = None) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
        }
        if category is not None:
            data['category'] = category
        self._client.request('POST', '/api/save', data=data)

    def unsave(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unsave', data=data)

    def hide(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/hide', data=data)

    def unhide(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unhide', data=data)
    '''
    def bulk_hide(self, submission_ids: Sequence[int]) -> CallChunkChainingIterator[int, None]:
        def mass_hide(ids: Sequence[int]) -> Sequence[SubmissionModel]:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('POST', '/api/hide', params={'id': ids_str})
            return [load_submission(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(
                CallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))



        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/hide', data=data)

    def bulk_unhide(self, submission_ids: Sequence[int]) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unhide', data=data)
    '''
    def mark_nsfw(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/marknsfw', data=data)

    def unmark_nsfw(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unmarknsfw', data=data)

    def mark_spoiler(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/markspoiler', data=data)

    def unmark_spoiler(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unmarkspoiler', data=data)

    def distinguish(self, submission_id: int) -> SubmissionModel:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'how': 'yes',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    def undistinguish(self, submission_id: int) -> SubmissionModel:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'how': 'no',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    def sticky(self, submission_id: int, slot: Optional[int] = None) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '1',
        }
        if slot is not None:
            data['slot'] = str(slot)
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def unsticky(self, submission_id: int) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '0',
        }
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def sticky_to_profile(self, submission_id: int, slot: Optional[int] = None) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '1',
            'to_profile': '1',
        }
        if slot is not None:
            data['slot'] = str(slot)
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def unsticky_from_profile(self, submission_id: int) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '0',
            'to_profile': '1',
        }
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def set_contest_mode(self, submission_id: int, state: bool) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '01'[state],
        }
        self._client.request('POST', '/api/set_contest_mode', data=data)

    def set_suggested_sort(self, submission_id: int, sort: Optional[str]) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
        }
        if sort is not None:
            data['sort'] = sort
        self._client.request('POST', '/api/set_suggested_sort', data=data)

    def enable_reply_notifications(self, submission_id: int) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '1'
        }
        self._client.request('POST', '/api/sendreplies', data=data)

    def disable_reply_notifications(self, submission_id: int) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '0'
        }
        self._client.request('POST', '/api/sendreplies', data=data)

    def set_event_time(self, submission_id: int, start: str, end: str, tz: str) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'event_start': start,
            'event_end': end,
            'event_tz': tz,
        }
        self._client.request('POST', '/api/event_post_time', data=data)

    def follow_event(self, submission_id: int) -> None:
        data = {
            'fullname': 't3_' + to_base36(submission_id),
            'follow': '1',
        }
        self._client.request('POST', '/api/follow_post', data=data)

    def unfollow_event(self, submission_id: int) -> None:
        data = {
            'fullname': 't3_' + to_base36(submission_id),
            'follow': '0',
        }
        self._client.request('POST', '/api/follow_post', data=data)

    def approve(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/approve', data=data)

    def remove(self, submission_id: int) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'spam': '0',
        }
        self._client.request('POST', '/api/remove', data=data)
