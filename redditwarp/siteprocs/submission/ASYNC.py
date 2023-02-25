
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, IO, Mapping, Union
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission, TextPost
    from ...models.comment_ASYNC import Comment
    from ...dtos.submission import GalleryItem
    from ...types import JSON_ro

import os.path as op
from functools import cached_property
import json

from ...model_loaders.submission_ASYNC import load_submission, load_text_post
from ...models.media_upload_lease import MediaUploadLease
from ...model_loaders.media_upload_lease import load_media_upload_lease
from ...http.payload import guess_filename_mimetype
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_async_iterator import CallChunkCallingAsyncIterator
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.submission_async1 import SubmissionSearchAsyncPaginator, SubmissionDuplicatesAsyncPaginator
from ...model_loaders.comment_ASYNC import load_comment
from .fetch_ASYNC import Fetch
from .get_ASYNC import Get

class SubmissionProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch: Fetch = Fetch(self, client)
        self.get: Get = Get(client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingAsyncIterator[Submission]:
        async def mass_fetch(ids: Sequence[int]) -> Sequence[Submission]:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = await self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_submission(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch, chunk) for chunk in chunked(ids, 100))

    async def reply(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't3_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/comment', files=dict(g()))
        return load_comment(result, self._client)

    class MediaUploading:
        def __init__(self, outer: SubmissionProcedures) -> None:
            self._client = outer._client

        async def __call__(self,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> MediaUploadLease:
            return await self.upload(file, filepath=filepath, timeout=timeout)

        async def obtain_upload_lease(self,
            *,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> MediaUploadLease:
            if mimetype is None:
                mimetype = guess_filename_mimetype(filepath)
            result = await self._client.request('POST', '/api/media/asset',
                    data={'filepath': filepath, 'mimetype': mimetype})
            return load_media_upload_lease(result)

        async def deposit_file(self,
            file: IO[bytes],
            upload_lease: MediaUploadLease,
            *,
            timeout: float = 1000,
        ) -> None:
            resp = await self._client.http.request('POST', upload_lease.endpoint,
                    data=upload_lease.fields, files={'file': file}, timeout=timeout)
            resp.raise_for_status()

        async def upload(self,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> MediaUploadLease:
            if filepath is None:
                filepath = op.basename(getattr(file, 'name', ''))
                if not filepath:
                    raise ValueError("the `filepath` parameter must be explicitly specified if the file object has no `name` attribute.")
            upload_lease = await self.obtain_upload_lease(filepath=filepath)
            await self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

    media_uploading: cached_property[MediaUploading] = cached_property(MediaUploading)

    async def create_text_post(self,
        sr: str,
        title: str,
        body: Union[str, Mapping[str, JSON_ro]],
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))
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

        root = await self._client.request('POST', '/api/submit', files=dict(g()))
        return int(root['json']['data']['id'], 36)

    async def create_link_post(self,
        sr: str,
        title: str,
        link: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
        resubmit: bool = True,
    ) -> int:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'link')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
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

        root = await self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    async def create_image_post(self,
        sr: str,
        title: str,
        link: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'image')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
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

        await self._client.request('POST', '/api/submit', data=dict(g()))

    async def create_video_post(self,
        sr: str,
        title: str,
        link: str,
        thumbnail: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
        vgif: bool = False,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'video' + ('gif' if vgif else ''))
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
            yield ('video_poster_url', thumbnail)
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

        await self._client.request('POST', '/api/submit', data=dict(g()))

    async def create_gallery_post(self,
        sr: str,
        title: str,
        items: Sequence[GalleryItem],
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        gallery_items: list[dict[str, str]] = [
            {
                'media_id': m.media_id,
                'caption': m.caption,
                'outbound_url': m.outbound_link,
            }
            for m in items
        ]

        def g() -> Iterable[tuple[str, JSON_ro]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('items', gallery_items)
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

        root = await self._client.request('POST', '/api/submit_gallery_post', json=dict(g()))
        return int(root['json']['data']['id'][3:], 36)

    async def create_poll_post(self,
        sr: str,
        title: str,
        body: str,
        options: Sequence[str],
        duration: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        def g() -> Iterable[tuple[str, JSON_ro]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('text', body)
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

        root = await self._client.request('POST', '/api/submit_poll_post', json=dict(g()))
        return int(root['json']['data']['id'][3:], 36)

    async def create_crosspost(self,
        sr: str,
        title: str,
        idn: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            yield ('crosspost_parent', 't3_' + to_base36(idn))
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

        root = await self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    async def edit_text_post_body(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> TextPost:
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't3_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/editusertext', files=dict(g()))
        return load_text_post(result, self._client)

    async def delete(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/del', data=data)

    async def lock(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/lock', data=data)

    async def unlock(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/unlock', data=data)

    async def vote(self, idn: int, direction: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'dir': str(direction),
        }
        await self._client.request('POST', '/api/vote', data=data)

    async def save(self, idn: int, category: Optional[str] = None) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
        }
        if category is not None:
            data['category'] = category
        await self._client.request('POST', '/api/save', data=data)

    async def unsave(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/unsave', data=data)

    async def hide(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/hide', data=data)

    async def unhide(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/unhide', data=data)

    def bulk_hide(self, ids: Iterable[int]) -> CallChunkCallingAsyncIterator[None]:
        async def mass_hide(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            await self._client.request('POST', '/api/hide', data={'id': ids_str})

        return CallChunkCallingAsyncIterator(AsyncCallChunk(mass_hide, chunk) for chunk in chunked(ids, 300))

    def bulk_unhide(self, ids: Iterable[int]) -> CallChunkCallingAsyncIterator[None]:
        async def mass_unhide(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            await self._client.request('POST', '/api/unhide', data={'id': ids_str})

        return CallChunkCallingAsyncIterator(AsyncCallChunk(mass_unhide, chunk) for chunk in chunked(ids, 300))

    async def mark_nsfw(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/marknsfw', data=data)

    async def unmark_nsfw(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/unmarknsfw', data=data)

    async def mark_spoiler(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/spoiler', data=data)

    async def unmark_spoiler(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/unspoiler', data=data)

    async def distinguish(self, idn: int) -> Submission:
        data = {
            'id': 't3_' + to_base36(idn),
            'how': 'yes',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    async def undistinguish(self, idn: int) -> Submission:
        data = {
            'id': 't3_' + to_base36(idn),
            'how': 'no',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    async def sticky(self, idn: int, slot: Optional[int] = None) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '1',
        }
        if slot is not None:
            data['num'] = str(slot)
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def unsticky(self, idn: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '0',
        }
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def pin_to_profile(self, idn: int, slot: Optional[int] = None) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'to_profile': '1',
            'state': '1',
        }
        if slot is not None:
            data['num'] = str(slot)
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def unpin_from_profile(self, idn: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'to_profile': '1',
            'state': '0',
        }
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def set_contest_mode(self, idn: int, state: bool) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '01'[state],
        }
        await self._client.request('POST', '/api/set_contest_mode', data=data)

    async def set_suggested_sort(self, idn: int, sort: str) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'sort': sort,
        }
        await self._client.request('POST', '/api/set_suggested_sort', data=data)

    async def enable_reply_notifications(self, idn: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '1'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def disable_reply_notifications(self, idn: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '0'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def set_event_time(self, idn: int,
            event_start: Optional[str] = None,
            event_end: Optional[str] = None,
            event_tz: Optional[str] = None) -> None:
        def g() -> Iterable[tuple[str, str]]:
            yield ('id', 't3_' + to_base36(idn))
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        await self._client.request('POST', '/api/event_post_time', data=dict(g()))

    async def follow_event(self, idn: int) -> None:
        data = {
            'fullname': 't3_' + to_base36(idn),
            'follow': '1',
        }
        await self._client.request('POST', '/api/follow_post', data=data)

    async def unfollow_event(self, idn: int) -> None:
        data = {
            'fullname': 't3_' + to_base36(idn),
            'follow': '0',
        }
        await self._client.request('POST', '/api/follow_post', data=data)

    async def approve(self, idn: int) -> None:
        data = {'id': 't3_' + to_base36(idn)}
        await self._client.request('POST', '/api/approve', data=data)

    async def remove(self, idn: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'spam': '0',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def remove_spam(self, idn: int) -> None:
        data = {
            'id': 't3_' + to_base36(idn),
            'spam': '1',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def ignore_reports(self, idn: int) -> None:
        await self._client.request('POST', '/api/ignore_reports', data={'id': 't3_' + to_base36(idn)})

    async def unignore_reports(self, idn: int) -> None:
        await self._client.request('POST', '/api/unignore_reports', data={'id': 't3_' + to_base36(idn)})

    async def snooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't3_' + to_base36(idn), 'reason': reason}
        await self._client.request('POST', '/api/snooze_reports', data=data)

    async def unsnooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't3_' + to_base36(idn), 'reason': reason}
        await self._client.request('POST', '/api/unsnooze_reports', data=data)

    async def apply_removal_reason(self,
            idn: int,
            reason_id: Optional[str] = None,
            note: Optional[str] = None) -> None:
        target = 't3_' + to_base36(idn)
        json_data = {'item_ids': [target], 'reason_id': reason_id, 'mod_note': note}
        await self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    async def send_removal_comment(self,
            idn: int,
            title: str,
            message: str,
            *,
            exposed: bool = False,
            locked: bool = False) -> Comment:
        target = 't3_' + to_base36(idn)
        json_data = {
            'type': 'public' + ('' if exposed else '_as_subreddit'),
            'item_id': [target],
            'title': title,
            'message': message,
            'lock_comment': '01'[locked],
        }
        root = await self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)
        return load_comment(root, self._client)

    async def send_removal_message(self,
            idn: int,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        target = 't3_' + to_base36(idn)
        json_data = {
            'type': 'private' + ('_exposed' if exposed else ''),
            'item_id': [target],
            'title': title,
            'message': message,
        }
        await self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)

    def search(self, sr: str, query: str, amount: Optional[int] = None, *,
        sort: str = 'relevance', time: str = 'all',
    ) -> ImpartedPaginatorChainingAsyncIterator[SubmissionSearchAsyncPaginator, Submission]:
        url = '/search'
        if sr:
            url = f'/r/{sr}/search'
        p = SubmissionSearchAsyncPaginator(
                self._client, url,
                params={'q': query, 'restrict_sr': '1'},
                    sort=sort, time=time)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def duplicates(self, target: int, amount: Optional[int] = None, *,
        sort: str = 'num_comments',
    ) -> ImpartedPaginatorChainingAsyncIterator[SubmissionDuplicatesAsyncPaginator, Submission]:
        subm_id = to_base36(target)
        p = SubmissionDuplicatesAsyncPaginator(self._client, f'/duplicates/{subm_id}', sort=sort)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
