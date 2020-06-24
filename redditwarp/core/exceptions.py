
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..http.response import Response
    from ..auth.token import Token

from .. import auth
from .. import user_agent

class RootException(Exception):
    pass

class BasicException(RootException):
    def __init__(self, exc_msg: object = None) -> None:
        super().__init__()
        self.exc_msg = exc_msg

    def __str__(self) -> str:
        if self.exc_msg is None:
            return self.exc_str()
        return str(self.exc_msg)

    def exc_str(self) -> str:
        return ''


class UnknownTokenType(BasicException):
    def __init__(self, exc_msg: object = None, *, token: Token):
        super().__init__(exc_msg)
        self.token = token

class ResponseException(BasicException):
    def __init__(self, exc_msg: object = None, *, response: Response) -> None:
        super().__init__(exc_msg)
        self.response = response

    def exc_str(self) -> str:
        return str(self.response)

class AuthError(ResponseException):
    pass

class CredentialsError(AuthError):
    pass

class InsufficientScope(AuthError):
    pass

class ResponseContentError(ResponseException):
    pass

class FaultyUserAgent(ResponseException):
    pass

class UnidentifiedResponseContentError(ResponseContentError):
    pass

class HTMLDocumentResponseContentError(ResponseContentError):
    pass

def get_exception_for_auth_response_content_error(resp: Response) -> ResponseException:
    if resp.data.lower().startswith(b'<!doctype html>'):
        msg = None
        if (b'<p>you are not allowed to do that</p>\n\n &mdash; access was denied to this resource.</div>' in resp.data):
            if resp.request is not None:
                ua = resp.request.headers['User-Agent']
                for i in user_agent.UA_BLACKLIST:
                    if i in ua:
                        msg = f'{i!r} is a known blacklisted user-agent pattern. Remove it from your user-agent string.'
                        break
        return HTMLDocumentResponseContentError(msg, response=resp)
    return UnidentifiedResponseContentError(response=resp)

def handle_auth_response_exception(e: auth.exceptions.ResponseException) -> None:
    if isinstance(e, auth.exceptions.ResponseContentError):
        raise get_exception_for_auth_response_content_error(e.response) from e

    elif isinstance(e, auth.exceptions.HTTPStatusError):
        status = e.response.status
        if status == 400:
            raise CredentialsError('check your grant credentials', response=e.response) from e

        elif status == 401:
            raise CredentialsError('check your client credentials', response=e.response) from e

        elif status == 403:
            if 'insufficient_scope' in e.response.headers.get('www-authenticate', ''):
                raise InsufficientScope('the request requires higher privileges than provided by your access token', response=e.response) from e

        elif status == 429:
            if e.response.request is not None:
                ua = e.response.request.headers['User-Agent']
                for i in user_agent.UA_FAULTY_LIST:
                    if i in ua:
                        raise FaultyUserAgent(
                            f'using {i!r} in your user-agent string is known to interfere with rate limits. Remove it from your user-agent string.',
                            response=e.response,
                        ) from e

    raise
