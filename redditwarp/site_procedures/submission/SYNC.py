
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, IO, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission as SubmissionModel
    from ...models.comment_SYNC import Comment

from functools import cached_property

from ...models.load.submission_SYNC import load_submission
from ...models.media_upload_lease import MediaUploadLease
from ...models.load.media_upload_lease import load_media_upload_lease
from ...http.payload import guess_mimetype_from_filename
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from ...models.load.comment_SYNC import load_comment
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

    class _upload_media:
        def __init__(self, outer: Submission):
            self._client = outer._client

        def __call__(self, file: IO[bytes]) -> MediaUploadLease:
            return self.upload(file)

        def obtain_upload_lease(self, filename: str, *, mimetype: Optional[str] = None) -> MediaUploadLease:
            if mimetype is None:
                mimetype = guess_mimetype_from_filename(filename)
            result = self._client.request('POST', '/api/media/asset',
                    data={'filepath': filename, 'mimetype': mimetype})
            return load_media_upload_lease(result)

        def deposit(self, upload_lease: MediaUploadLease, file: IO[bytes]) -> None:
            sess = self._client.http.session
            req = sess.make_request('POST', upload_lease.endpoint, data=upload_lease.fields, files={'file': file})
            resp = sess.send(req, timeout=-1)
            resp.raise_for_status()

        def upload(self, file: IO[bytes]) -> MediaUploadLease:
            upload_lease = self.obtain_upload_lease(file.name)
            self.deposit(upload_lease, file)
            return upload_lease

    upload_media = cached_property(_upload_media)

    def create_text_post(self,
        sr: str,
        title: str,
        text: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: str = '',
        flair_uuid: str = '',
        flair_text: str = '',
        event_start: str = '',
        event_end: str = '',
        event_tz: str = '',
    ) -> int:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            yield ('text', text)
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    def create_link_post(self,
        sr: str,
        title: str,
        url: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: str = '',
        flair_uuid: str = '',
        flair_text: str = '',
        event_start: str = '',
        event_end: str = '',
        event_tz: str = '',
        resubmit: bool = True,
    ) -> int:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'link')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', url)
            if resubmit: yield ('resubmit', '1')
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    def create_image_post(self,
        sr: str,
        title: str,
        image_url: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: str = '',
        flair_uuid: str = '',
        flair_text: str = '',
        event_start: str = '',
        event_end: str = '',
        event_tz: str = '',
    ) -> int:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'image')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', image_url)
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    def create_video_post(self,
        sr: str,
        title: str,
        video_upload_lease: MediaUploadLease,
        thumbnail_upload_lease: MediaUploadLease,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: str = '',
        flair_uuid: str = '',
        flair_text: str = '',
        event_start: str = '',
        event_end: str = '',
        event_tz: str = '',
        vgif: bool = False,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'videogif' if vgif else 'video')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', video_upload_lease.resource_location)
            yield ('video_poster_url', thumbnail_upload_lease.resource_location)
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        self._client.request('POST', '/api/submit', data=dict(g()))

    def create_gallery_post(self,
        sr: str,
        title: str,
        items: Sequence[Mapping[str, str]],
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: str = '',
        flair_uuid: str = '',
        flair_text: str = '',
        event_start: str = '',
        event_end: str = '',
        event_tz: str = '',
    ) -> int:
        def g() -> Iterable[tuple[str, object]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('items', items)
            yield ('sendreplies', reply_notifications)
            if spoiler: yield ('spoiler', True)
            if nsfw: yield ('nsfw', True)
            if oc: yield ('original_content', True)
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit_gallery_post', json=dict(g()))
        return int(root['json']['data']['id'][3:], 36)

    def create_poll_post(self,
        sr: str,
        title: str,
        text: str,
        options: Sequence[str],
        duration: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        collection_uuid: str = '',
        flair_uuid: str = '',
        flair_text: str = '',
        event_start: str = '',
        event_end: str = '',
        event_tz: str = '',
    ) -> int:
        def g() -> Iterable[tuple[str, object]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('text', text)
            yield ('options', options)
            yield ('duration', duration)
            yield ('sendreplies', reply_notifications)
            if spoiler: yield ('spoiler', True)
            if nsfw: yield ('nsfw', True)
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit_poll_post', json=dict(g()))
        return int(root['json']['data']['id'][3:], 36)

    def edit_post_text(self, submission_id: int, text: str) -> SubmissionModel:
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

    def bulk_hide(self, submission_ids: Sequence[int]) -> CallChunkCallingIterator[Sequence[int], None]:
        def mass_hide(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            self._client.request('POST', '/api/hide', params={'id': ids_str})

        return CallChunkCallingIterator(
                CallChunk(mass_hide, idfs) for idfs in chunked(submission_ids, 300))

    def bulk_unhide(self, submission_ids: Sequence[int]) -> CallChunkCallingIterator[Sequence[int], None]:
        def mass_hide(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            self._client.request('POST', '/api/unhide', params={'id': ids_str})

        return CallChunkCallingIterator(
                CallChunk(mass_hide, idfs) for idfs in chunked(submission_ids, 300))

    def mark_nsfw(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/marknsfw', data=data)

    def unmark_nsfw(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unmarknsfw', data=data)

    def mark_spoiler(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/spoiler', data=data)

    def unmark_spoiler(self, submission_id: int) -> None:
        data = {'id': 't3_' + to_base36(submission_id)}
        self._client.request('POST', '/api/unspoiler', data=data)

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

    def pin_to_profile(self, submission_id: int, slot: Optional[int] = None) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'state': '1',
            'to_profile': '1',
        }
        if slot is not None:
            data['slot'] = str(slot)
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def unpin_from_profile(self, submission_id: int) -> None:
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

    def set_event_time(self, submission_id: int,
            event_start: str, event_end: str, event_tz: str) -> None:
        data = {
            'id': 't3_' + to_base36(submission_id),
            'event_start': event_start,
            'event_end': event_end,
            'event_tz': event_tz,
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

    def ignore_reports(self, idn: int) -> None:
        self._client.request('POST', '/api/ignore_reports', data={'id': 't3_' + to_base36(idn)})

    def unignore_reports(self, idn: int) -> None:
        self._client.request('POST', '/api/unignore_reports', data={'id': 't3_' + to_base36(idn)})

    def snooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't3_' + to_base36(idn), 'reason': reason}
        self._client.request('POST', '/api/snooze_reports', data=data)

    def unsnooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't3_' + to_base36(idn), 'reason': reason}
        self._client.request('POST', '/api/unsnooze_reports', data=data)

    def set_removal_reason(self,
            submission_id: int,
            reason_id: Optional[int],
            note: Optional[str] = None) -> None:
        target = 't3_' + to_base36(submission_id)
        reason = None if reason_id is None else to_base36(reason_id)
        json_data = {'item_ids': [target], 'reason_id': reason, 'mod_note': note}
        self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    def send_removal_comment(self,
            submission_id: int,
            title: str,
            message: str) -> Comment:
        target = 't3_' + to_base36(submission_id)
        json_data = {'type': 'public', 'item_id': [target], 'title': title, 'message': message}
        root = self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)
        return load_comment(root, self._client)

    def send_removal_modmail(self,
            submission_id: int,
            title: str,
            message: str,
            *,
            expose: bool = False) -> None:
        target = 't3_' + to_base36(submission_id)
        json_data = {
            'type': 'private' + ('_exposed' if expose else ''),
            'item_id': [target],
            'title': title,
            'message': message,
        }
        self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)
