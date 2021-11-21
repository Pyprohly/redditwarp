
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Mapping
if TYPE_CHECKING:
    from .http.response import Response

from . import http

class ArgExcMixin(Exception):
    def __init__(self, arg: object = None) -> None:
        super().__init__()
        self.arg: object = arg

    def __str__(self) -> str:
        if self.arg is None:
            return self.get_default_message()
        return str(self.arg)

    def get_default_message(self) -> str:
        return ''

class ArgExc(ArgExcMixin):
    pass


class ClientException(ArgExc):
    pass

class NoResultException(ClientException):
    pass

class ResultRejectedException(ClientException):
    pass


class _Throwaway(ArgExc):
    pass

class UserAgentRequired(_Throwaway):
    pass


def raise_for_non_json_response(resp: Response) -> None:
    data = resp.data
    is_html_content = resp.headers.get('Content-Type', '').startswith('text/html')

    if is_html_content:
        if b"user agent required" in data:
            raise UserAgentRequired('the Reddit API wants you to set a user agent')

    try:
        resp.raise_for_status()
    except http.exceptions.StatusCodeException as e:
        if is_html_content:
            msg = None
            if b"Our CDN was unable to reach our servers" in data:
                msg = 'HTML, "Our CDN was unable to reach our servers"'
            if b"title>reddit.com: page not found</title" in data:
                msg = 'HTML, page not found'
            e.arg = msg
        raise


class APIError(ArgExc):
    pass

class RedditError(APIError):
    def __init__(self,
        arg: object = None,
        *,
        codename: str,
        explanation: str,
        field: str,
    ) -> None:
        super().__init__(arg)
        self.codename: str = codename
        self.explanation: str = explanation
        self.field: str = field

    def get_default_message(self) -> str:
        co = self.codename
        xp = self.explanation
        fd = self.field
        if co:
            if xp:
                if fd:
                    return f'{co}: {xp} -> {fd}'
                return f'{co}: {xp}'
            if fd:
                return f'{co} -> {fd}'
            return co
        return ''


def raise_for_reddit_error(json_data: Any) -> None:
    if not isinstance(json_data, Mapping):
        return

    error_record: Sequence[Any]
    if (
        isinstance(codename := json_data.get('reason'), str)
        and isinstance(explanation := json_data.get('explanation'), str)
        and isinstance(field := next(iter(json_data.get('fields', [])), None), str)
    ):
        raise RedditError(codename=codename, explanation=explanation, field=field)
    elif (
        isinstance(codename := json_data.get('reason'), str)
        and json_data.get('explanation') is None
        and isinstance(field := next(iter(json_data.get('fields', [])), None), str)
    ):
        raise RedditError(codename=codename, explanation='', field=field)
    elif (
        isinstance(reason := json_data.get('reason'), str)
        and json_data.get('explanation') is None
        and list(json_data.get('fields', [])) == [None]
    ):
        raise RedditError(codename=reason, explanation='', field='')
    elif (
        isinstance(codename := json_data.get('reason'), str)
        and isinstance(explanation := json_data.get('explanation'), str)
    ):
        raise RedditError(codename=codename, explanation=explanation, field='')
    elif json_data.keys() >= {'error', 'message'} and isinstance(reason := json_data.get('reason'), str):
        raise RedditError(codename=reason, explanation='', field='')
    elif json_data.keys() >= {'error', 'message'}:
        return  # No useful information. Treat this as a StatusCodeException.
    elif json_data.keys() >= {'message'} and isinstance(reason := json_data.get('reason'), str):
        raise RedditError(codename=reason, explanation='', field='')
    elif (
        (error_record := next(iter(json_data.get('json', {}).get('errors', [])), [None, None, None]))
        and isinstance(codename := error_record[0], str)
        and isinstance(explanation := error_record[1], str)
        and isinstance(field := error_record[2], str)
    ):
        raise RedditError(codename=codename, explanation=explanation, field=field)
    elif (
        (error_record := next(iter(json_data.get('json', {}).get('errors', [])), [None, None, None]))
        and isinstance(codename := error_record[0], str)
        and isinstance(explanation := error_record[1], str)
    ):
        raise RedditError(codename=codename, explanation=explanation, field='')
    elif (
        isinstance(codename := next(iter(json_data.get('errors', [])), None), str)
        and isinstance(explanation := next(iter(json_data.get('errors_values', [])), None), str)
    ):
        raise RedditError(codename=codename, explanation=explanation, field='')
