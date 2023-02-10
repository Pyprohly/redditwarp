
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Tuple
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.flair import FlairTemplate, FlairChoices, UserFlairAssociation

import csv
from io import StringIO

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.flair_sync1 import UserFlairAssociationPaginator
from ...model_loaders.flair import (
    load_variant2_flair_template,
    load_variant1_flair_template,
    load_flair_choices,
    load_user_flair_association,
)

class FlairProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def assign_user_flair(self, sr_name: str, name: str,
            text: Optional[str] = None, css_class: Optional[str] = None) -> None:
        d = {'name': name}
        if text is not None:
            d['text'] = text
        if css_class is not None:
            d['css_class'] = css_class
        self._client.request('POST', f'/r/{sr_name}/api/flair', data=d)

    def assign_post_flair(self, sr_name: str, submission_id: int,
            text: Optional[str] = None, css_class: Optional[str] = None) -> None:
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

    def bulk_update_user_flairs(self,
        sr_name: str,
        data: Iterable[Tuple[str, str, str]],
    ) -> CallChunkChainingIterator[bool]:
        def mass_update_user_flairs(data: Sequence[Tuple[str, str, str]]) -> Sequence[bool]:
            sio = StringIO()
            csv.writer(sio).writerows(data)
            s = sio.getvalue()
            root = self._client.request('POST', f'/r/{sr_name}/api/flaircsv', data={'flair_csv': s})
            return [i['ok'] for i in root]

        itr = map(
            lambda xs: CallChunk(mass_update_user_flairs, xs),
            chunked(data, 100),
        )
        return CallChunkChainingIterator(itr)

    def _create_or_update_flair_template(self,
        sr: str,
        flair_type: str,
        *,
        uuid: Optional[str] = None,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        user_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        d = {'flair_type': flair_type}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
            ('mod_only', None if mod_only is None else '01'[mod_only]),
            ('text_editable', None if user_editable is None else '01'[user_editable]),
            ('allowable_content', allowable_content),
            ('max_emojis', str(max_emojis)),
        ):
            if v is not None:
                d[k] = v
        root = self._client.request('POST', f'/r/{sr}/api/flairtemplate_v2', data=d)
        return load_variant2_flair_template(root)

    def create_user_flair_template(self,
        sr: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        user_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            user_editable=user_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def create_post_flair_template(self,
        sr: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        user_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return self._create_or_update_flair_template(
            sr,
            flair_type='POST_FLAIR',
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            user_editable=user_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def update_user_flair_template(self,
        sr: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        user_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            user_editable=user_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def update_post_flair_template(self,
        sr: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        user_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            user_editable=user_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def assign_user_flair_template(self,
        sr: str,
        user: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
    ) -> None:
        d = {'name': user}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
        ):
            if v is not None:
                d[k] = v
        self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    def assign_post_flair_template(self,
        sr: str,
        submission_id: int,
        uuid: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
    ) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        d = {'link': full_id36}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
        ):
            if v is not None:
                d[k] = v
        self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

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
        sr_name: str,
        *,
        user_flair_enabled: Optional[bool],
        user_flair_position: Optional[str],
        user_flair_self_assign: Optional[bool],
        post_flair_position: Optional[str],
        post_flair_self_assign: Optional[bool],
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            if user_flair_enabled is not None:
                yield ('flair_enabled', '01'[user_flair_enabled])
            if user_flair_position is not None:
                yield ('flair_position', user_flair_position)
            if user_flair_self_assign is not None:
                yield ('flair_self_assign_enabled', '01'[user_flair_self_assign])
            if post_flair_position is not None:
                yield ('link_flair_position', post_flair_position)
            if post_flair_self_assign is not None:
                yield ('link_flair_self_assign_enabled', '01'[post_flair_self_assign])

        self._client.request('POST', f'/r/{sr_name}/api/flairconfig', data=dict(g()))

    def reorder_user_flair_templates(self, sr_name: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr_name, 'flair_type': 'USER_FLAIR'}
        self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    def reorder_post_flair_templates(self, sr_name: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr_name, 'flair_type': 'POST_FLAIR'}
        self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    def get_user_flair_templates(self, sr_name: str) -> Sequence[FlairTemplate]:
        root = self._client.request('GET', f'/r/{sr_name}/api/user_flair_v2')
        return [load_variant1_flair_template(i) for i in root]

    def get_post_flair_templates(self, sr_name: str) -> Sequence[FlairTemplate]:
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
    ) -> ImpartedPaginatorChainingIterator[UserFlairAssociationPaginator, UserFlairAssociation]:
        p = UserFlairAssociationPaginator(self._client, f'/r/{sr_name}/api/flairlist')
        return ImpartedPaginatorChainingIterator(p, amount)

    def show_my_flair(self, sr_name: str) -> None:
        self._client.request('GET', f'/r/{sr_name}/api/setflairenabled', params={'flair_enabled': '1'})

    def hide_my_flair(self, sr_name: str) -> None:
        self._client.request('GET', f'/r/{sr_name}/api/setflairenabled', params={'flair_enabled': '0'})
