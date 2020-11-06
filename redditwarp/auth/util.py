
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping
    from .client_credentials import ClientCredentials
    from ..http.request import Request

from base64 import b64encode
from urllib.parse import urlencode

from . import grants

def __authorization_url(  # UNUSED: scrapped idea
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
    return f'{url}?{urlencode(params)}'

def basic_auth(client_credentials: ClientCredentials) -> str:
    ci = client_credentials.client_id
    cs = client_credentials.client_secret
    return 'Basic ' + b64encode(f'{ci}:{cs}'.encode()).decode()

def apply_basic_auth(request: Request, client_credentials: ClientCredentials) -> None:
    request.headers['Authorization'] = basic_auth(client_credentials)

def auto_grant_factory(
    refresh_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> Optional[grants.AuthorizationGrant]:
    """Produce a simple non-expiring grant from the provided credentials.

    Return either:

        * Refresh Token
        * Resource Owner Password Credentials
        * Client Credentials
    """
    if refresh_token:
        return grants.RefreshTokenGrant(refresh_token)
    if username and password:
        return grants.ResourceOwnerPasswordCredentialsGrant(username, password)
    if username or password:
        return None
    return grants.ClientCredentialsGrant()
