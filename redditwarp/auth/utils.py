
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping, MutableMapping

from base64 import b64encode
from urllib.parse import urlencode

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
        scheme: str = 'Basic') -> str:
    """Make a basic auth string suitable for use in an `Authorization` header."""
    b64_user_pass = b64encode(f"{userid}:{password}".encode()).decode()
    return f"{scheme} {b64_user_pass}"

def apply_basic_auth(
    headers: MutableMapping[str, str],
    userid: str,
    password: str,
    *,
    scheme: str = 'Basic',
    header_name: str = 'Authorization',
) -> None:
    """Write a basic auth string into the `Authorization` field of a headers mapping."""
    headers[header_name] = basic_auth(userid, password, scheme=scheme)
