"""Reddit API specific constants."""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Set

AUTHORIZATION_BASE_URL: str = "https://www.reddit.com"
AUTHORIZATION_ENDPOINT_PATH: str = "/api/v1/authorize"
AUTHORIZATION_URL: str = AUTHORIZATION_BASE_URL + AUTHORIZATION_ENDPOINT_PATH
MOBILE_AUTHORIZATION_ENDPOINT_PATH: str = AUTHORIZATION_ENDPOINT_PATH + ".compact"
MOBILE_AUTHORIZATION_URL: str = AUTHORIZATION_BASE_URL + MOBILE_AUTHORIZATION_ENDPOINT_PATH
TOKEN_OBTAINMENT_ENDPOINT_PATH: str = "/api/v1/access_token"
TOKEN_OBTAINMENT_URL: str = AUTHORIZATION_BASE_URL + TOKEN_OBTAINMENT_ENDPOINT_PATH
TOKEN_REVOCATION_ENDPOINT_PATH: str = "/api/v1/revoke_token"
TOKEN_REVOCATION_URL: str = AUTHORIZATION_BASE_URL + TOKEN_REVOCATION_ENDPOINT_PATH

RESOURCE_BASE_URL: str = "https://oauth.reddit.com"

TRUSTED_ORIGINS: Set[str] = {
    RESOURCE_BASE_URL,
    "https://gateway.reddit.com",
}
