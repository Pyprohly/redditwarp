
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Mapping
if TYPE_CHECKING:
    from .http.response import Response

class ArgExcMixin(Exception):
    def __init__(self, arg: object = None) -> None:
        super().__init__()
        self.arg: object = arg

    def __str__(self) -> str:
        if self.arg is None:
            return self.get_default_message()
        return str(self.arg)

    def get_default_message(self) -> str:
        """Get a default exception message for this exception type."""
        return ''

class ArgExc(ArgExcMixin):
    pass


class OperationException(ArgExc):
    """A class of exceptions for when the client needs to raise an exception."""

class NoResultException(OperationException):
    """Raised when a requested target does not exist."""

class RejectedResultException(OperationException):
    """Raised when a returned value does not fulfil an invariant."""

class UnexpectedResultException(OperationException):
    """Raised when a certain result was not expected."""


class _Throwaway(ArgExc):
    pass

class UserAgentRequired(_Throwaway):
    """Raised when the client detects that the Reddit API wants you to set a user agent."""


def raise_for_non_json_response(resp: Response) -> None:
    """Raise exceptions for a HTTP response from Reddit that does not contain JSON.

    This function assumes the given response object does not contain JSON.
    """
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


class APIError(OperationException):
    """A formal API-specified error."""

class RedditError(APIError):
    """

    Errors from Reddit's API typically consist of three pieces of information:
    an error label, an explanation, and the name of a related parameter field.

    .. ATTRIBUTES

    .. attribute:: label
        :type: str

        A label for the error. E.g., `USER_REQUIRED`, `INVALID_OPTION`, `SUBREDDIT_NOEXIST`.
        In rare cases this label may not always be in uppercase. It can even contain spaces.
        The value may be an empty string.

    .. attribute:: explanation
        :type: str

        A description for the error.
        The value may be an empty string.

    .. attribute:: field
        :type: str

        The name of the parameter relevant to the error, if applicable.
        The value may be an empty string.
    """

    __match_args__ = ('label',)

    def __init__(self,
        arg: object = None,
        *,
        label: str,
        explanation: str,
        field: str,
    ) -> None:
        super().__init__(arg)
        self.label: str = label
        self.explanation: str = explanation
        self.field: str = field

    def get_default_message(self) -> str:
        la = self.label
        xp = self.explanation
        fd = self.field
        if la:
            if xp:
                if fd:
                    return f'{la}: {xp} -> {fd}'
                return f'{la}: {xp}'
            if fd:
                return f'{la} -> {fd}'
            return la
        return ''


def raise_for_reddit_error(json_data: Any) -> None:
    """Examine JSON data returned from the API and raise appropriate exceptions if
    any API errors were detected.

    This function is the default `snub` parameter value for the
    :meth:`Client.request <.client_SYNC.Client.request>` method.
    """
    if not isinstance(json_data, Mapping):
        return

    error_record: Sequence[Any]
    if (
        isinstance(label := json_data.get('reason'), str)
        and isinstance(explanation := json_data.get('explanation'), str)
        and isinstance(field := next(iter(json_data.get('fields', [])), None), str)
    ):
        raise RedditError(label=label, explanation=explanation, field=field)
    elif (
        isinstance(label := json_data.get('reason'), str)
        and json_data.get('explanation') is None
        and isinstance(field := next(iter(json_data.get('fields', [])), None), str)
    ):
        raise RedditError(label=label, explanation='', field=field)
    elif (
        isinstance(reason := json_data.get('reason'), str)
        and json_data.get('explanation') is None
        and list(json_data.get('fields', [])) == [None]
    ):
        raise RedditError(label=reason, explanation='', field='')
    elif (
        isinstance(label := json_data.get('reason'), str)
        and isinstance(explanation := json_data.get('explanation'), str)
    ):
        raise RedditError(label=label, explanation=explanation, field='')
    elif json_data.keys() >= {'error', 'message'} and isinstance(reason := json_data.get('reason'), str):
        raise RedditError(label=reason, explanation='', field='')
    elif json_data.keys() >= {'error', 'message'}:
        return  # No useful information. Treat this as a StatusCodeException.
    elif json_data.keys() >= {'message'} and isinstance(reason := json_data.get('reason'), str):
        raise RedditError(label=reason, explanation='', field='')
    elif (
        (error_record := next(iter(json_data.get('json', {}).get('errors', [])), [None, None, None]))
        and isinstance(label := error_record[0], str)
        and isinstance(explanation := error_record[1], str)
        and isinstance(field := error_record[2], str)
    ):
        raise RedditError(label=label, explanation=explanation, field=field)
    elif (
        (error_record := next(iter(json_data.get('json', {}).get('errors', [])), [None, None, None]))
        and isinstance(label := error_record[0], str)
        and isinstance(explanation := error_record[1], str)
    ):
        raise RedditError(label=label, explanation=explanation, field='')
    elif (
        isinstance(label := next(iter(json_data.get('errors', [])), None), str)
        and isinstance(explanation := next(iter(json_data.get('errors_values', [])), None), str)
    ):
        raise RedditError(label=label, explanation=explanation, field='')


from . import http  # Avoid cyclic import
