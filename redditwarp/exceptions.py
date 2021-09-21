
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, List, Sequence, Mapping
if TYPE_CHECKING:
    from .http.response import Response

from dataclasses import dataclass
from http import HTTPStatus

from . import http

class ArgInfoExceptionMixin(Exception):
    def __init__(self, arg: object = None) -> None:
        super().__init__()
        self.arg = arg

    def __str__(self) -> str:
        if self.arg is None:
            return self.get_default_message()
        return str(self.arg)

    def get_default_message(self) -> str:
        return ''

class ArgInfoException(ArgInfoExceptionMixin):
    pass


class ClientException(ArgInfoException):
    pass

class NoResultException(ClientException):
    pass

class ResultRejectedException(ClientException):
    pass


class ResponseException(ArgInfoException):
    def __init__(self, arg: object = None, *, response: Response):
        super().__init__(arg)
        self.response = response

class HTTPStatusError(ResponseException):
    pass

def raise_for_status(resp: Response) -> None:
    try:
        resp.raise_for_status()
    except http.exceptions.StatusCodeException:
        sts = resp.status
        msg = str(sts)
        try:
            msg = f"{sts} {HTTPStatus(sts).phrase}"
        except ValueError:
            pass
        raise HTTPStatusError(msg, response=resp) from None


class ResponseContentError(ResponseException):
    """A base exception class denoting that something in the response body
    from an API request is amiss. Either an error was indicated by the API
    or the structure is of something the client isn't prepared to handle,
    so the response was rejected.
    """

class UnidentifiedResponseContentError(ResponseContentError):
    """The response body contains data that the client isn't prepared to handle."""


class UnacceptableHTMLDocumentReceivedError(ResponseContentError):
    pass


def raise_for_response_content_error(resp: Response) -> None:
    content_type = resp.headers.get('Content-Type', '')
    if content_type.startswith('text/html'):
        msg = None
        data = resp.data
        if b'user agent required' in data:
            msg = 'the Reddit API wants you to set a user agent'
        if b'Our CDN was unable to reach our servers' in data:
            msg = '"Our CDN was unable to reach our servers"'
        if b'title>reddit.com: page not found</title' in data:
            msg = 'page not found'
        raise UnacceptableHTMLDocumentReceivedError(msg, response=resp)

def handle_non_json_response(resp: Response) -> Exception:
    raise_for_response_content_error(resp)
    raise_for_status(resp)
    raise UnidentifiedResponseContentError(response=resp)
    return Exception

def raise_for_json_object_data(resp: Response, data: Mapping[str, Any]) -> None:
    raise_for_variant1_reddit_api_error(resp, data)
    raise_for_variant2_reddit_api_error(resp, data)


class ApplicationException(ResponseException):
    """The remote API wishes to formally inform the client that a service request was carried
    out unsuccessfully."""

class RedditAPIError(ApplicationException):
    def __init__(self,
        arg: object = None, *,
        response: Response,
        codename: str,
        detail: str,
        field: str,
    ) -> None:
        super().__init__(arg=arg, response=response)
        self.codename = codename
        self.detail = detail
        self.field = field

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({self.response})>'

    def get_default_message(self) -> str:
        return f"{self.codename}: {self.detail}"

class Variant1RedditAPIError(RedditAPIError):
    def __init__(self,
        arg: object = None, *,
        response: Response,
        codename: str,
        detail: str,
        fields: Sequence[str],
    ):
        super().__init__(
            arg=arg,
            response=response,
            codename=codename,
            detail=detail,
            field=fields[0] if fields else '',
        )
        self.fields = fields

    def get_default_message(self) -> str:
        cn = self.codename
        de = self.detail
        fd = self.field
        return f"{cn}: {de}{fd and f' -> {fd}'}"

def raise_for_variant1_reddit_api_error(resp: Response, data: Mapping[str, Any]) -> None:
    if data.keys() >= {'explanation', 'reason'}:
        codename = data['reason']
        detail = data['explanation']
        fields = data.get('fields', ())
        raise Variant1RedditAPIError(
            response=resp,
            codename=codename,
            detail=detail,
            fields=fields,
        )

class Variant2RedditAPIError(RedditAPIError):
    """An error class denoting an error that was indicated in the
    response body of an API request, occurring when the remote API
    wishes to inform the client that a service request was carried
    out unsuccessfully.
    """

    def __init__(self, arg: object = None, *, response: Response, errors: Sequence[RedditErrorItem]):
        """
        Parameters
        ----------
        response: :class:`.http.Response`
        errors: List[:class:`.RedditErrorItem`]
        """
        err = errors[0]
        super().__init__(
            arg=arg,
            response=response,
            codename=err.codename,
            detail=err.detail,
            field=err.field,
        )
        self.errors = errors

    def __repr__(self) -> str:
        err_names = [err.codename for err in self.errors]
        return f'<{self.__class__.__name__} ({self.response}) {err_names}>'

    def get_default_message(self) -> str:
        err_count = len(self.errors)
        if err_count > 1:
            return "(multiple errors encountered):\n" \
                    + '\n'.join(
                        f"  {err.codename}: {err.detail}{err.field and f' -> {err.field}'}"
                        for err in self.errors)

        cn = self.codename
        de = self.detail
        fd = self.field
        return f"{cn}: {de}{fd and f' -> {fd}'}"

@dataclass
class RedditErrorItem:
    codename: str
    detail: str
    field: str

def try_parse_reddit_error_items(data: Mapping[str, Any]) -> Optional[List[RedditErrorItem]]:
    errors = data.get('json', {}).get('errors')
    if errors:
        l = []
        for e in errors:
            name, message, field = e
            l.append(RedditErrorItem(name, message, field or ''))
        return l
    return None

def raise_for_variant2_reddit_api_error(resp: Response, data: Mapping[str, Any]) -> None:
    error_list = try_parse_reddit_error_items(data)
    if error_list is not None:
        raise Variant2RedditAPIError(response=resp, errors=error_list)
