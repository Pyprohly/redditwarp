
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..http.response import Response
    from ..auth.token import Token

from .. import auth
from ..auth.const import TOKEN_OBTAINMENT_URL
from ..http.util.case_insensitive_dict import CaseInsensitiveDict

class RootException(Exception):
    pass

class InfoException(RootException):
    def __init__(self, arg: object = None) -> None:
        super().__init__()
        self.arg = arg

    def __str__(self) -> str:
        if self.arg is None:
            return self.get_default_message()
        return str(self.arg)

    def get_default_message(self) -> str:
        return ''


class UnknownTokenType(InfoException):
    def __init__(self, arg: object = None, *, token: Token):
        super().__init__(arg)
        self.token = token

class ResponseException(InfoException):
    def __init__(self, arg: object = None, *, response: Response) -> None:
        super().__init__(arg)
        self.response = response

    def get_default_message(self) -> str:
        return str(self.response)

class AuthError(ResponseException):
    pass

class CredentialsError(AuthError):
    pass

class InsufficientScope(AuthError):
    pass

class ResponseContentError(ResponseException):
    pass


class BadUserAgent(ResponseException):
    pass

class BlacklistedUserAgent(ResponseException):
    pass

class FaultyUserAgent(ResponseException):
    pass


class UnidentifiedResponseContentError(ResponseContentError):
    pass

class HTMLDocumentResponseContentError(ResponseContentError):
    pass

def handle_auth_response_exception(e: auth.exceptions.ResponseException) -> None:
    resp = e.response
    status = resp.status

    if isinstance(e, auth.exceptions.ResponseContentError):
        if status == 403:
            if resp.request is not None:
                ua = resp.request.headers['User-Agent']
                msg = None

                if ua.startswith('Bot'):
                    msg = "User agent strings must not start with the string 'Bot'"

                for s in (
                    'scraping',
                    'searchme',
                ):
                    if s in ua:
                        msg = f'{s!r} is a known blacklisted user-agent pattern. Remove it from your user-agent string.'
                        break

                raise BlacklistedUserAgent(msg, response=resp) from e

        if resp.data.lower().startswith(b'<!doctype html>'):
            raise HTMLDocumentResponseContentError(response=resp) from e
        raise UnidentifiedResponseContentError(response=resp) from e

    elif isinstance(e, auth.exceptions.HTTPStatusError):
        if status == 400:
            raise CredentialsError('check your grant credentials', response=resp) from e

        elif status == 401:
            if resp.request:
                uri = resp.request.uri
                if not uri.startswith("https://www.reddit.com"):
                    e.arg = f'access token URL inaccuracy: got {uri!r}, need {TOKEN_OBTAINMENT_URL!r}'
                    raise
            raise CredentialsError('check your client credentials', response=resp) from e

        elif status == 403:
            if 'insufficient_scope' in resp.headers.get('www-authenticate', ''):
                raise InsufficientScope('the request requires higher privileges than provided by your access token', response=resp) from e

        elif status == 429:
            if resp.request is not None:
                ua = resp.request.headers['User-Agent']
                if 'curl' in ua:
                    raise FaultyUserAgent(
                        "the pattern 'curl' in your user-agent string is known to interfere with rate limits. Remove it from your user-agent string.",
                        response=resp,
                    ) from e

    elif isinstance(e, auth.exceptions.UnsupportedGrantType):
        if resp.request:
            headers = CaseInsensitiveDict(resp.request.headers)
            if 'Content-Type' in headers:
                content_type = resp.request.headers.get('Content-Type', '')
                expected_content_type = 'application/x-www-form-urlencoded'
                if not content_type.startswith(expected_content_type):
                    e.arg = f'bad Content-Type header: got {content_type!r}, need {expected_content_type!r}'

    raise
