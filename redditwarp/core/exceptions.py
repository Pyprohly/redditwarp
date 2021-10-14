
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..http.request import Request
    from ..http.response import Response

from .. import auth
from ..auth.const import TOKEN_OBTAINMENT_URL
from .. import http
from ..http.util.case_insensitive_dict import CaseInsensitiveDict
from ..exceptions import ArgExcMixin
from ..auth.exceptions import raise_for_token_server_response_error

class ArgExc(ArgExcMixin):
    pass


def raise_for_reddit_token_server_response_error(json_dict: Any) -> None:
    error = json_dict.get('error')
    if not isinstance(error, str):
        return
    raise_for_token_server_response_error(json_dict)


class _Throwaway(ArgExc):
    pass

class AuthError(_Throwaway):
    pass

class CredentialsError(_Throwaway):
    pass

class ClientCredentialsError(CredentialsError):
    pass

class GrantCredentialsError(CredentialsError):
    pass

class BlacklistedUserAgent(_Throwaway):
    pass

class FaultyUserAgent(_Throwaway):
    pass


def raise_for_reddit_auth_response_exception(e: Exception, req: Request, resp: Response) -> None:
    req_headers = CaseInsensitiveDict(req.headers)

    if isinstance(e, auth.exceptions.TokenServerResponseError):
        if e.error_name == 'invalid_grant':
            raise GrantCredentialsError('Check your grant credentials')

        elif e.error_name == 'unsupported_grant_type':
            content_type = req_headers.get('Content-Type', '')
            expected_content_type = 'application/x-www-form-urlencoded'
            if content_type != expected_content_type:
                raise AuthError(f'bad Content-Type header: got {content_type!r}, need {expected_content_type!r}')

    elif isinstance(e, http.exceptions.StatusCodeException):
        status = e.status_code
        if status == 401:
            if not (url := req.uri).startswith("https://www.reddit.com"):
                raise AuthError(f'bad access token URL: got {url!r}, need {TOKEN_OBTAINMENT_URL!r}')
            if 'Authorization' not in req_headers:
                raise AuthError('Authorization header missing from request')
            if not req_headers['Authorization'][:5].lower().startswith('basic'):
                raise AuthError('Authorization header value must start with "Basic"')
            raise ClientCredentialsError('Check your client credentials')

        if status == 403:
            msg = None
            ua = req_headers['User-Agent']
            if ua.startswith('Bot'):
                msg = "User-Agent strings must not start with 'Bot'."
            for s in ['scraping', 'searchme']:
                if s in ua:
                    msg = f"{s!r} is a known blacklisted User-Agent pattern. Remove it from your User-Agent string."
                    break
            raise BlacklistedUserAgent(msg)

        elif status == 429:
            ua = req_headers['User-Agent']
            if 'curl' in ua:
                msg = "The pattern 'curl', in your User-Agent string, is known to interfere with rate limits. Remove it from your User-Agent string."
                raise FaultyUserAgent(msg)
