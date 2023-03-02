
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Tuple
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.flair import FlairTemplate, FlairTemplateChoices, UserFlairAssociation

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
    load_flair_template_choices,
    load_user_flair_association,
)

class FlairProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def set_user_flair(self,
        sr: str,
        user: str,
        text: Optional[str],
        css_class: Optional[str] = None,
    ) -> None:
        """Set the flair information on a user.

        Any previously set flair information will be discarded.

        A null argument means the field will not be sent in the request.
        The API treats this as the same as supplying an empty string.

        To revoke a flair, specify null or an empty string for the `text`
        and `css_class` parameters.

        .. .PARAMETERS

        :param `str` sr:
            Subreddit name.
        :param `str` user:
            User name.
        :param `Optional[str]` text:
            Flair text.

            Specify a string no longer than 64 characters.
            If longer than 64 characters then the parameter is ignored and an empty string is used.
        :param `Optional[str]` css_class:
            Flair CSS class.

            Specify a string no longer than 100 characters.
            If longer than 100 characters then a `BAD_CSS_NAME` API error is returned.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `BAD_FLAIR_TARGET`:
                The specified user doesn't exist.
            + `BAD_CSS_NAME`:
               - The specified CSS class was longer than 100 characters.
               - The specified CSS class contained invalid characters.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have permission to set flairs in the specified subreddit.

            + `404`:
                The specified subreddit does not exist.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('name', user)
            if text is not None: yield ('text', text)
            if css_class is not None: yield ('css_class', css_class)

        self._client.request('POST', f'/r/{sr}/api/flair', data=dict(g()))

    def set_post_flair(self,
        sr: str,
        subm: int,
        text: Optional[str],
        css_class: Optional[str] = None,
    ) -> None:
        """Set the flair information on a post.

        Any previously set flair information will be discarded.

        A null argument means the field will not be sent in the request.
        The API treats this as the same as supplying an empty string.

        To revoke a flair, specify null or an empty string for the `text`
        and `css_class` parameters.

        .. .PARAMETERS

        :param `str` sr:
            Subreddit name.
        :param `int` subm:
            Submission ID.
        :param `Optional[str]` text:
            Flair text.

            Specify a string no longer than 64 characters.
            If longer than 64 characters then the parameter is ignored and an empty string is used.
        :param `Optional[str]` css_class:
            Flair CSS class.

            Specify a string no longer than 100 characters.
            If longer than 100 characters then a `BAD_CSS_NAME` API error is returned.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `BAD_FLAIR_TARGET`:
                The specified submission doesn't exist.
            + `BAD_CSS_NAME`:
               - The specified CSS class was longer than 100 characters.
               - The specified CSS class contained invalid characters.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have permission to set flairs in the specified subreddit.
               - The target submission does not belong to the specified subreddit.

            + `404`:
                The specified subreddit does not exist.
        """
        full_id36 = 't3_' + to_base36(subm)

        def g() -> Iterable[tuple[str, str]]:
            yield ('link', full_id36)
            if text is not None: yield ('text', text)
            if css_class is not None: yield ('css_class', css_class)

        self._client.request('POST', f'/r/{sr}/api/flair', data=dict(g()))

    def bulk_set_user_flairs(self,
        sr: str,
        items: Iterable[Tuple[str, str, str]],
    ) -> CallChunkChainingIterator[bool]:
        """Bulk set flair information for users.

        The second parameter is an iterable of 3-element tuples:
        `(user, text, css_class)`: the target user name, the flair text,
        and CSS class to assign.

        .. .PARAMETERS

        :param `str` sr:
        :param `Iterable[tuple[str, str, str]]` items:
            An iterable of tuples consisting of `(user, text, css_class)`.

        .. .RETURNS

        :returns:
            For each input item, a boolean appears in the output indicating whether
            the flair assignment succeeded.
        :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[`bool`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have permission to set flairs in the specified subreddit.

            + `404`:
                The specified subreddit does not exist.
        """
        def mass_update_user_flairs(items: Sequence[Tuple[str, str, str]]) -> Sequence[bool]:
            sio = StringIO()
            csv.writer(sio).writerows(items)
            s = sio.getvalue()
            root = self._client.request('POST', f'/r/{sr}/api/flaircsv', files={'flair_csv': s})
            return [d['ok'] for d in root]

        itr = map(
            lambda xs: CallChunk(mass_update_user_flairs, xs),
            chunked(items, 100),
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
        text_editable: Optional[bool] = None,
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
            ('text_editable', None if text_editable is None else '01'[text_editable]),
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
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        """Create a user flair template.

        Any previously set flair information will be discarded.

        A null argument means the field will not be sent in the request.
        The API treats this as the same as supplying an empty string.

        .. .PARAMETERS

        :param `str` sr:
        :param `Optional[str]` text:
        :param `Optional[str]` css_class:
        :param `Optional[str]` bg_color:
            A 6-digit rgb hex color with an optional hash at the start. E.g. `#fb8559`.

            For user flair templates, the background color can be unset, making it transparent.
            (Post flairs cannot be transparent.)

            Effective default: empty string. It will be transparent.
        :param `Optional[str]` fg_color_scheme:
            Either `dark` or `light`.

            Effective default: `dark`.
        :param `Optional[bool]` mod_only:
            Whether flair is only available for mods to select.

            Effective default: false.
        :param `Optional[bool]` text_editable:
            Whether users will be able to edit their flair text.

            Effective default: false.
        :param `Optional[str]` allowable_content:
            Either: `all`, `emoji`, `text`.

            Effective default: `all`.
        :param `Optional[int]` max_emojis:
            An integer from 1 to 10.

            Effective default: `10`.

        .. .RETURNS

        :returns: The newly created flair template.
        :rtype: :class:`~.models.flair.FlairTemplate`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have permission to set flairs in the specified subreddit.

            + `404`:
                The specified subreddit does not exist.
        """
        return self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
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
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        """Create a post flair template.

        Behaves similarly to :meth:`.create_user_flair_template`.

        .. .PARAMETERS

        :(parameters):
            Same as :meth:`.create_user_flair_template`,
            but `bg_color` effective default is different.

        :param `Optional[str]` bg_color:
            Effective default: `#d3d6da`.

        .. .RETURNS

        :(returns): Same as :meth:`.create_user_flair_template`.

        .. .RAISES

        :(raises): Same as :meth:`.create_user_flair_template`.
        """
        return self._create_or_update_flair_template(
            sr,
            flair_type='LINK_FLAIR',
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
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
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        """Update a user flair template.

        Behaves similarly to :meth:`.create_user_flair_template`.

        .. .PARAMETERS

        :(parameters):
            Similar to :meth:`.create_user_flair_template`.

        :param `str` uuid:
            The flair template UUID.
        """
        return self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
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
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        """Update a post flair template.

        Behaves similarly to :meth:`.update_user_flair_template`.
        """
        return self._create_or_update_flair_template(
            sr,
            flair_type='LINK_FLAIR',
            uuid=uuid,
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def delete_flair_template(self, sr: str, uuid: str) -> None:
        """Delete a user or post flair template.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have permission.

            + `404`:
               - The specified subreddit does not exist.
               - The specified flair UUID does not exist.
        """
        self._client.request('POST', f'/r/{sr}/api/deleteflairtemplate', data={'flair_template_id': uuid})

    def delete_all_user_flair_templates(self, sr: str) -> None:
        """Delete all user flair templates in a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have permission.

            + `404`:
                The specified subreddit does not exist.
        """
        self._client.request('POST', f'/r/{sr}/api/clearflairtemplates', data={'flair_type': 'USER_FLAIR'})

    def delete_all_post_flair_templates(self, sr: str) -> None:
        """Delete all post flair templates in a subreddit."""
        self._client.request('POST', f'/r/{sr}/api/clearflairtemplates', data={'flair_type': 'LINK_FLAIR'})

    def retrieve_user_flair_templates(self, sr: str) -> Sequence[FlairTemplate]:
        """Return a list of available user flair templates in a subreddit.

        Current user must be a moderator of the subreddit
        (otherwise a 403 HTTP error is returned).

        For non-mods, there is :meth:`.get_post_flair_choices`.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.flair.FlairTemplate`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                The specified subreddit does not exist.
            + `403`:
                You do not have permission.
        """
        root = self._client.request('GET', f'/r/{sr}/api/user_flair_v2')
        return [load_variant1_flair_template(d) for d in root]

    def retrieve_post_flair_templates(self, sr: str) -> Sequence[FlairTemplate]:
        """Return a list of available post flair templates in a subreddit.

        Behaves similarly to :meth:`.retrieve_user_flair_templates`.
        """
        root = self._client.request('GET', f'/r/{sr}/api/link_flair_v2')
        return [load_variant1_flair_template(d) for d in root]

    def reorder_user_flair_templates(self, sr: str, order: Sequence[str]) -> None:
        """Reorder user flair templates.

        Reorders the flair templates as shown in the UI.

        The list must contain every flair UUID, otherwise a 400 HTTP error is returned.

        If you duplicate an ID the flair will have multiple references in the UI.

        .. .PARAMETERS

        :param `str` sr:
        :param `Sequence[str]` order:
            A list of all flair UUIDs.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                A flair template ID is missing from the provided list.
            + `500`:
                The specified subreddit does not exist.
        """
        params = {'subreddit': sr, 'flair_type': 'USER_FLAIR'}
        self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    def reorder_post_flair_templates(self, sr: str, order: Sequence[str]) -> None:
        """Reorder post flair templates.

        Behaves similarly to :meth:`.reorder_user_flair_templates`.
        """
        params = {'subreddit': sr, 'flair_type': 'LINK_FLAIR'}
        self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    def assign_user_flair_template(self,
        sr: str,
        user: str,
        uuid: str,
        *,
        text: Optional[str] = None,
    ) -> None:
        """Assign a user flair template.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `str` uuid:
        :param `Optional[str]` text:
            Custom text to override the template's text.

            Supply `None` or empty string to use the template's text.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The specified flair UUID does not exist.
               - You do not have permission.

            + `404`:
               - The specified subreddit does not exist.
               - The specified user does not exist.
        """
        d = {
            'name': user,
            'flair_template_id': uuid,
        }
        if text is not None:
            d['text'] = text
        self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    def assign_post_flair_template(self,
        sr: str,
        subm: int,
        uuid: str,
        *,
        text: Optional[str] = None,
    ) -> None:
        """Assign a post flair template.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `str` uuid:
        :param `Optional[str]` text:
            Custom text to override the template's text.

            Supply `None` or empty string to use the template's text.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The specified flair UUID does not exist.
               - You do not have permission.

            + `404`:
               - The specified subreddit does not exist.
               - The specified submission does not exist.
        """
        full_id36 = 't3_' + to_base36(subm)
        d = {
            'link': full_id36,
            'flair_template_id': uuid,
        }
        if text is not None:
            d['text'] = text
        self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    def assign_user_flair(self,
        sr: str,
        user: str,
        text: Optional[str],
        css_class: Optional[str] = None,
        *,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
    ) -> None:
        """Assign a custom user flair.

        This is a newer version of :meth:`.set_user_flair`.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Optional[str]` text:
        :param `Optional[str]` css_class:
        :param `Optional[str]` bg_color:
        :param `Optional[str]` fg_color_scheme:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `BAD_CSS_NAME`:
               - The specified CSS class was longer than 100 characters.
               - The specified CSS class contained invalid characters.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `404`:
               - The specified subreddit does not exist.
               - The specified user does not exist.
        """
        d = {'name': user}
        for k, v in (
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
        ):
            if v is not None:
                d[k] = v
        self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    def assign_post_flair(self,
        sr: str,
        subm: int,
        text: Optional[str],
        css_class: Optional[str] = None,
        *,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
    ) -> None:
        """Assign a custom post flair.

        This is a newer version of :meth:`.set_user_flair`.

        .. .PARAMETERS

        :param `str` sr:
        :param `int` subm:
        :param `Optional[str]` text:
        :param `Optional[str]` css_class:
        :param `Optional[str]` bg_color:
        :param `Optional[str]` fg_color_scheme:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `BAD_CSS_NAME`:
               - The specified CSS class was longer than 100 characters.
               - The specified CSS class contained invalid characters.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `404`:
               - The specified subreddit does not exist.
               - The specified submission does not exist.
        """
        full_id36 = 't3_' + to_base36(subm)
        d = {'link': full_id36}
        for k, v in (
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
        ):
            if v is not None:
                d[k] = v
        self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    def configure_subreddit_flair_settings(self,
        sr: str,
        *,
        user_enabled: Optional[bool] = False,
        user_position: Optional[str] = '',
        user_self_assign: Optional[bool] = False,
        post_position: Optional[str] = '',
        post_self_assign: Optional[bool] = False,
    ) -> None:
        """Configure subreddit flair settings.

        All parameters should be specified. If a parameter is not specified or is
        an invalid value, its default will be used.

        User flairs are disabled when either `user_enabled` is false
        or `user_position` is an empty string.

        Post flairs are disabled when `post_position` is an empty string.

        .. .PARAMETERS

        :param `str` sr:
        :param `Optional[bool]` user_enabled:
            Whether user flairs are enabled in the subreddit.

            Effective default: false.
        :param `Optional[str]` user_position:
            Either `left`, `right`, or empty string.

            An empty string value will disable user flairs even if
            `user_enabled` is true.

            Effective default: empty string.
        :param `Optional[bool]` user_self_assign:
            Whether users are allowed to assign their own user flairs.

            Value is forced false if `user_enabled` is false
            (but not if `user_position` is an empty string).

            Effective default: false.
        :param `Optional[str]` post_position:
            Either `left`, `right`, or empty string.

            Effective default: empty string.
        :param `Optional[bool]` post_self_assign:
            Whether users are allowed to assign their own post flairs.

            Value is forced false if `post_position` is an empty string.

            Effective default: false.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `404`:
                The specified subreddit does not exist.
        """
        def g() -> Iterable[tuple[str, str]]:
            if user_enabled is not None:
                yield ('flair_enabled', '01'[user_enabled])
            if user_position is not None:
                yield ('flair_position', user_position)
            if user_self_assign is not None:
                yield ('flair_self_assign_enabled', '01'[user_self_assign])
            if post_position is not None:
                yield ('link_flair_position', post_position)
            if post_self_assign is not None:
                yield ('link_flair_self_assign_enabled', '01'[post_self_assign])

        self._client.request('POST', f'/r/{sr}/api/flairconfig', data=dict(g()))

    def get_user_flair_template_choices(self, sr: str) -> FlairTemplateChoices:
        """Get user flair template choices.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :returns: :class:`~.models.flair.FlairTemplateChoices`, a `Sequence`\\[:class:`~.models.flair.FlairTemplateChoice`]
        :rtype: :class:`~.models.flair.FlairTemplateChoices`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                There is no user context.
            + `404`:
                The specified subreddit does not exist.
        """
        root = self._client.request('POST', f'/r/{sr}/api/flairselector')
        return load_flair_template_choices(root)

    def get_post_flair_template_choices(self, sr: str) -> FlairTemplateChoices:
        """Get user flair template choices.

        Behaves similarly to :meth:`.get_user_flair_template_choices`.
        """
        root = self._client.request('POST', f'/r/{sr}/api/flairselector', data={'is_newlink': '1'})
        return load_flair_template_choices(root)

    def get_user_flair_association(self, sr: str, user: str) -> Optional[UserFlairAssociation]:
        """Get a user flair association in a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.flair.UserFlairAssociation`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                The specified subreddit does not exist.
            + `403`:
               - There is no user context.
               - You are not a moderator of the subreddit.
        """
        params = {'name': user, 'limit': '1'}
        root = self._client.request('GET', f'/r/{sr}/api/flairlist', params=params)
        users_data = root['users']
        if not users_data:
            return None
        user_data = users_data[0]
        if user_data['user'].lower() != user.lower():
            return None
        return load_user_flair_association(user_data)

    def get_user_flair_associations(self,
        sr: str,
        amount: Optional[int] = None,
    ) -> ImpartedPaginatorChainingIterator[UserFlairAssociationPaginator, UserFlairAssociation]:
        """Get a user flair associations in a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.flair_sync1.UserFlairAssociationPaginator`, :class:`~.models.flair.UserFlairAssociation`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                The specified subreddit does not exist.
            + `403`:
               - There is no user context.
               - You are not a moderator of the subreddit.
        """
        p = UserFlairAssociationPaginator(self._client, f'/r/{sr}/api/flairlist')
        return ImpartedPaginatorChainingIterator(p, amount)

    def show_my_flair(self, sr: str) -> None:
        """Show the current user's flair in the subreddit.

        To tell if the current user's flair is shown::

           subr = client.p.subreddit.fetch_by_name('Python')
           print(subr.me.flair.shown)

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `404`:
                The specified subreddit does not exist.
        """
        self._client.request('POST', f'/r/{sr}/api/setflairenabled', params={'flair_enabled': '1'})

    def hide_my_flair(self, sr: str) -> None:
        """Hide the current user's flair in the subreddit."""
        self._client.request('POST', f'/r/{sr}/api/setflairenabled', params={'flair_enabled': '0'})
