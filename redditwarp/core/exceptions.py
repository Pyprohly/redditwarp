
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..http.request import Request
    from ..http.response import Response

from .. import auth
from ..auth.const import TOKEN_OBTAINMENT_URL
from .. import http
from ..http.util.case_insensitive_dict import CaseInsensitiveDict
from ..exceptions import ArgInfoExceptionMixin
from ..auth.exceptions import raise_for_token_server_response_error

class ArgInfoException(ArgInfoExceptionMixin):
    pass


def raise_for_reddit_token_server_response_error(json_dict: Any) -> None:
    error = json_dict.get('error')
    if not isinstance(error, str):
        return
    raise_for_token_server_response_error(json_dict)


class ResponseContentError(ArgInfoException):
    pass

class UnidentifiedResponseContentError(ResponseContentError):
    pass

class HTMLDocumentResponseContentError(ResponseContentError):
    pass

class CredentialsError(ArgInfoException):
    pass

class ClientCredentialsError(CredentialsError):
    pass

class GrantCredentialsError(CredentialsError):
    pass

class BadUserAgent(ArgInfoException):
    pass

class BlacklistedUserAgent(BadUserAgent):
    pass

class FaultyUserAgent(BadUserAgent):
    pass

def handle_reddit_auth_response_exception(e: Exception, req: Request, resp: Response) -> Exception:
    headers = CaseInsensitiveDict(req.headers)

    if isinstance(e, ValueError):
        if resp.status == 403:
            msg = None
            ua = headers['User-Agent']
            if ua.startswith('Bot'):
                msg = "User agent strings must not start with the string 'Bot'"
            for s in 'scraping searchme'.split():
                if s in ua:
                    msg = f"{s!r} is a known blacklisted user-agent pattern. Remove it from your user-agent string."
                    break
            raise BlacklistedUserAgent(msg) from e

        if resp.headers.get('Content-Type', '').startswith('text/html'):
            msg = None
            if b'Our CDN was unable to reach our servers' in resp.data:
                msg = '"Our CDN was unable to reach our servers"'
            raise HTMLDocumentResponseContentError(msg) from e
        raise UnidentifiedResponseContentError from e

    elif isinstance(e, auth.exceptions.TokenServerResponseError):
        if e.error_name == 'invalid_grant':
            raise GrantCredentialsError('Check your grant credentials') from e

        elif e.error_name == 'unsupported_grant_type':
            content_type = headers.get('Content-Type', '')
            expected_content_type = 'application/x-www-form-urlencoded'
            if content_type != expected_content_type:
                e.arg = f'bad Content-Type header: got {content_type!r}, need {expected_content_type!r}'

    elif isinstance(e, http.exceptions.StatusCodeException):
        if resp.status == 401:
            if not (url := req.uri).startswith("https://www.reddit.com"):
                e.arg = f'bad access token URL: got {url!r}, need {TOKEN_OBTAINMENT_URL!r}'
                raise e
            if 'Authorization' not in headers:
                e.arg = 'Authorization header missing from request'
                raise e
            if not headers['Authorization'][:5].lower().startswith('basic'):
                e.arg = 'Authorization header value must start with "Basic"'
                raise e
            raise ClientCredentialsError('Check your client credentials') from e

        elif resp.status == 429:
            ua = headers['User-Agent']
            if 'curl' in ua:
                msg = "The pattern 'curl', in your user-agent string, is known to interfere with rate limits. Remove it from your user-agent string."
                raise FaultyUserAgent(msg) from e

    raise e
    return Exception
