
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, List, Sequence, Tuple, Callable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.flair import Variant2FlairTemplate, Variant1FlairTemplate, FlairChoices, UserFlairAssociation
    from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
    from ...iterators.paginators.flair.flair_associations_paginator import FlairAssociationsPaginator

import csv
from io import StringIO

from ...util.base_conversion import to_base36
from ...iterators.chunking_iterator import ChunkingIterator
from ...iterators.call_chunk_chaining_iterator import ChunkSizeAdjustableCallChunkChainingIterator
from ...models.load.flair import (
    load_variant2_flair_template,
    load_variant1_flair_template,
    load_flair_choices,
    load_user_flair_association,
)

class Flair:
    def __init__(self, client: Client):
        self._client = client

    def assign_user_flair(self, sr_name: str, name: str, text: Optional[str], css_class: Optional[str]) -> None:
        d = {'name': name}
        if text is not None:
            d['text'] = text
        if css_class is not None:
            d['css_class'] = css_class
        self._client.request('POST', f'/r/{sr_name}/api/flair', data=d)

    def assign_post_flair(self, sr_name: str, submission_id: int, text: Optional[str], css_class: Optional[str]) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        d = {'link': full_id36}
        if text is not None:
            d['text'] = text
        if css_class is not None:
            d['css_class'] = css_class
        self._client.request('POST', f'/r/{sr_name}/api/flair', data=d)

    def revoke_user_flair(self, sr_name: str, name: str) -> None:
        self._client.request('POST', f'/r/{sr_name}/api/flair', data=dict(name=name))

    def revoke_post_flair(self, sr_name: str, submission_id: int) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        self._client.request('POST', f'/r/{sr_name}/api/flair', data=dict(link=full_id36))

    def bulk_update_user_flairs(self, sr_name: str, data: Iterable[Tuple[str, str, str]]) -> Iterable[bool]:
        chunk_iter = ChunkingIterator(data, 100)

        def call_chunk(data_chunk: Iterable[Tuple[str, str, str]]) -> Callable[[], List[bool]]:
            def f() -> List[bool]:
                sio = StringIO()
                csv.writer(sio).writerows(data_chunk)
                s = sio.getvalue()
                root = self._client.request('POST', f'/r/{sr_name}/api/flaircsv', data={'flair_csv': s})
                return [i['ok'] for i in root]
            return f

        call_chunks = map(call_chunk, chunk_iter)
        return ChunkSizeAdjustableCallChunkChainingIterator(call_chunks, chunk_iter)

    def _create_or_update_flair_template(self,
        sr_name: str,
        *,
        flair_type: str,
        uuid: Optional[str] = None,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        text_color: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
        override_css: Optional[bool] = None,
    ) -> Variant2FlairTemplate:
        d = {'flair_type': flair_type}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('allowable_content', allowable_content),
            ('background_color', bg_color),
            ('css_class', css_class),
            ('text_color', text_color),
            ('text_editable', None if text_editable is None else '01'[text_editable]),
            ('max_emojis', str(max_emojis)),
            ('mod_only', None if mod_only is None else '01'[mod_only]),
            ('override_css', None if override_css is None else '01'[override_css]),
        ):
            if v is not None:
                d[k] = v
        root = self._client.request('POST', f'/r/{sr_name}/api/flairtemplate_v2', data=d)
        return load_variant2_flair_template(root)

    def create_user_flair_template(self,
        sr_name: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        text_color: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
        override_css: Optional[bool] = None,
    ) -> Variant2FlairTemplate:
        return self._create_or_update_flair_template(
            sr_name,
            flair_type='USER_FLAIR',
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            text_color=text_color,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
            override_css=override_css,
        )

    def create_post_flair_template(self,
        sr_name: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        text_color: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
        override_css: Optional[bool] = None,
    ) -> Variant2FlairTemplate:
        return self._create_or_update_flair_template(
            sr_name,
            flair_type='POST_FLAIR',
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            text_color=text_color,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
            override_css=override_css,
        )

    def update_user_flair_template(self,
        sr_name: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        text_color: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
        override_css: Optional[bool] = None,
    ) -> Variant2FlairTemplate:
        return self._create_or_update_flair_template(
            sr_name,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            text_color=text_color,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
            override_css=override_css,
        )

    def update_post_flair_template(self,
        sr_name: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        text_color: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
        override_css: Optional[bool] = None,
    ) -> Variant2FlairTemplate:
        return self._create_or_update_flair_template(
            sr_name,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            text_color=text_color,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
            override_css=override_css,
        )

    def assign_user_flair_template(self,
        sr_name: str,
        name: str,
        uuid: Optional[str],
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
    ) -> None:
        d = {'name': name}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', text_color),
        ):
            if v is not None:
                d[k] = v
        self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=d)

    def assign_post_flair_template(self,
        sr_name: str,
        submission_id: int,
        uuid: Optional[str],
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
    ) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        d = {'link': full_id36}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', text_color),
        ):
            if v is not None:
                d[k] = v
        self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=d)

    def revoke_user_flair_template(self, sr_name: str, name: str) -> None:
        self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=dict(name=name))

    def revoke_post_flair_template(self, sr_name: str, submission_id: int) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=dict(link=full_id36))

    def delete_user_flair_template(self, sr_name: str, uuid: str) -> None:
        self._client.request('POST', f'/r/{sr_name}/api/deleteflairtemplate',
                data=dict(flair_template_id=uuid))

    def delete_post_flair_template(self, sr_name: str, uuid: str) -> None:
        self.delete_user_flair_template(sr_name, uuid)

    def delete_all_user_flair_templates(self, sr_name: str) -> None:
        self._client.request('POST', f'/r/{sr_name}/api/clearflairtemplates', data={'flair_type': 'USER_FLAIR'})

    def delete_all_post_flair_templates(self, sr_name: str) -> None:
        self._client.request('POST', f'/r/{sr_name}/api/clearflairtemplates', data={'flair_type': 'POST_FLAIR'})

    def configure_subreddit_flair_settings(self,
        *,
        u_enabled: Optional[bool],
        u_position: Optional[str],
        u_self_assign: Optional[bool],
        #,
        p_position: Optional[str],
        p_self_assign: Optional[bool],
    ) -> None:
        d = {}
        for k, v in {
            'flair_enabled': None if u_enabled is None else '01'[u_enabled],
            'flair_position': u_position,
            'flair_self_assign_enabled': None if u_self_assign is None else '01'[u_self_assign],
            'link_flair_position': p_position,
            'link_flair_self_assign_enabled': None if p_self_assign is None else '01'[p_self_assign],
        }.items():
            if v is not None:
                d[k] = v
        self._client.request('POST', '/r/{sr_name}/api/flairconfig', data=d)

    def reorder_user_flair_templates(self, sr_name: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr_name, 'flair_type': 'USER_FLAIR'}
        self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    def reorder_post_flair_templates(self, sr_name: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr_name, 'flair_type': 'POST_FLAIR'}
        self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    def get_user_flair_templates(self, sr_name: str) -> Sequence[Variant1FlairTemplate]:
        root = self._client.request('GET', f'/r/{sr_name}/api/user_flair_v2')
        return [load_variant1_flair_template(i) for i in root]

    def get_post_flair_templates(self, sr_name: str) -> Sequence[Variant1FlairTemplate]:
        root = self._client.request('GET', f'/r/{sr_name}/api/link_flair_v2')
        return [load_variant1_flair_template(i) for i in root]

    def get_user_flair_choices(self, sr_name: str, name: Optional[str]) -> Optional[FlairChoices]:
        d = {}
        if name is not None:
            d['name'] = name
        root = self._client.request('POST', f'/r/{sr_name}/api/flairselector', data=d)
        if root == '{}':
            return None
        return load_flair_choices(root)

    def get_post_flair_choices(self, sr_name: str, submission_id: Optional[int]) -> Optional[FlairChoices]:
        d = {'is_newlink': '1'}
        if submission_id is not None:
            full_id36 = to_base36(submission_id)
            d['link'] = full_id36
        root = self._client.request('POST', f'/r/{sr_name}/api/flairselector', data=d)
        if root == '{}':
            return None
        return load_flair_choices(root)

    def get_user_flair_association(self, sr_name: str, name: str) -> Optional[UserFlairAssociation]:
        params = {'name': name, 'limit': '1'}
        root = self._client.request('GET', f'/r/{sr_name}/api/flairlist', params=params)
        users_data = root['users']
        if not users_data:
            return None
        user_data = users_data[0]
        if user_data['user'].lower() != name.lower():
            return None
        return load_user_flair_association(user_data)

    def get_user_flair_associations(self,
        sr_name: str,
        amount: Optional[int] = None,
    ) -> PaginatorChainingIterator[FlairAssociationsPaginator, UserFlairAssociation]:
        p = FlairAssociationsPaginator(self._client, '/r/{sr_name}/api/flairlist')
        return PaginatorChainingIterator(p, amount)

    def show_my_flair(self, sr_name: str) -> None:
        self._client.request('GET', f'/r/{sr_name}/api/setflairenabled', params={'flair_enabled': '1'})

    def hide_my_flair(self, sr_name: str) -> None:
        self._client.request('GET', f'/r/{sr_name}/api/setflairenabled', params={'flair_enabled': '0'})
