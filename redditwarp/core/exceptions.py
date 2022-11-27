
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..http.exchange import Exchange

from .. import auth
from .const import TOKEN_OBTAINMENT_URL
from .. import http
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
    """These exceptions are not intended to be caught."""

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


def raise_for_reddit_auth_response_exception(e: Exception, xchg: Exchange) -> None:
    requ_headers = xchg.request.headers

    if isinstance(e, auth.exceptions.TokenServerResponseError):
        if e.error_name == 'invalid_grant':
            msg = 'Check your grant credentials'
            pld = xchg.requisition.payload
            if isinstance(pld, http.payload.URLEncodedFormData):
                grant = pld.data
                if grant.get('grant_type') == 'password':
                    msg = "Check your grant credentials.\n\nTip: If you have 2FA enabled the password grant won't work. You must use a refresh token instead."
            raise GrantCredentialsError(msg)

        elif e.error_name == 'unsupported_grant_type':
            content_type = requ_headers.get('Content-Type', '')
            expected_content_type = 'application/x-www-form-urlencoded'
            if content_type != expected_content_type:
                raise AuthError(f'bad Content-Type header: got {content_type!r}, need {expected_content_type!r}')

    elif isinstance(e, http.exceptions.StatusCodeException):
        status = e.status_code
        if status == 400:
            pld = xchg.requisition.payload
            if isinstance(pld, http.payload.URLEncodedFormData):
                grant = pld.data
                if grant.get('grant_type') == 'refresh_token':
                    e.arg = "Your refresh token might be invalid."
                    raise e

        elif status == 401:
            if not (url := xchg.requisition.url).startswith(("https://www.reddit.com", "https://ssl.reddit.com")):
                raise AuthError(f'bad access token URL: got {url!r}, need {TOKEN_OBTAINMENT_URL!r}')
            if 'Authorization' not in requ_headers:
                raise AuthError('Authorization header missing from request')
            if not requ_headers['Authorization'][:5].lower().startswith('basic'):
                raise AuthError('Authorization header value must start with "Basic"')
            raise ClientCredentialsError('Check your client credentials')

        elif status == 403:
            ua = requ_headers['User-Agent']
            if ua.startswith('Bot'):
                raise BlacklistedUserAgent("User-Agent strings must not start with 'Bot'.")
            for s in ['scraping', 'searchme']:
                if s in ua:
                    raise BlacklistedUserAgent(
                        f"{s!r} is a known blacklisted User-Agent pattern."
                        " Remove it from your User-Agent string."
                    )

        elif status == 404:
            pld = xchg.requisition.payload
            if isinstance(pld, http.payload.URLEncodedFormData):
                grant = pld.data
                if grant.get('grant_type') == 'authorization_code':
                    e.arg = "The authorization code might be expired."
                    raise e

        elif status == 429:
            ua = requ_headers['User-Agent']
            if 'curl' in ua:
                msg = "The pattern 'curl' in your User-Agent string is known to interfere with rate limits. Remove it from your User-Agent string."
                raise FaultyUserAgent(msg)
