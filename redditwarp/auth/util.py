
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping
    from ..http.request import Request

from base64 import b64encode
from urllib.parse import urlencode

from . import grants

def ___authorization_url(  # UNUSED: scrapped idea
    url: str,
    response_type: str,
    client_id: str,
    redirect_uri: Optional[str],
    scope: Optional[str] = None,
    state: Optional[str] = None,
    extra_params: Optional[Mapping[str, str]] = None,
) -> str:
    params = {
        'response_type': response_type,
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state,
        **(extra_params or {}),
    }
    params = {k: v for k, v in params.items() if v}
    return '%s?%s' % (url, urlencode(params))


def basic_auth(userid: str, password: str, *,
        scheme: str = "Basic") -> str:
    b64_user_pass = b64encode(f"{userid}:{password}".encode()).decode()
    return f"{scheme} {b64_user_pass}"

def apply_basic_auth(
    request: Request,
    userid: str,
    password: str,
    *,
    scheme: str = "Basic",
    header: str = "Authorization",
) -> None:
    request.headers[header] = basic_auth(userid, password, scheme=scheme)


def auto_grant_factory(
    refresh_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> grants.AuthorizationGrant:
    """Produce an authorization grant from the provided credentials."""
    if refresh_token:
        if username or password:
            raise ValueError("`refresh_token` cannot be used with `username` or `password`")
        return grants.RefreshTokenGrant(refresh_token)
    if username and password:
        return grants.ResourceOwnerPasswordCredentialsGrant(username, password)
    if username or password:
        raise ValueError("cannot create an authorization grant from the provided credentials")
    return grants.ClientCredentialsGrant()
