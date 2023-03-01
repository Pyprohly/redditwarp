
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Set
    from ...types import JSON_ro

from ...core.const import RESOURCE_BASE_URL

# Although the authorisation system used by Reddit's internal API is not
# OAuth2-spec compliant, there are similarities in the way credentials are used.

REDDIT_MOBILE_ANDROID_CLIENT_ID: str = 'ohXpoqrZYub1kg'
REDDIT_MOBILE_IOS_CLIENT_ID: str = 'LNDo9k1o8UAEUw'

ACCOUNTS_BASE_URL: str = "https://accounts.reddit.com"
TOKEN_OBTAINMENT_ENDPOINT_PATH: str = "/api/access_token"
TOKEN_OBTAINMENT_URL: str = ACCOUNTS_BASE_URL + TOKEN_OBTAINMENT_ENDPOINT_PATH

GRANT_DATA: JSON_ro = {"scopes":["*","email","pii"]}


GRAPHQL_BASE_URL: str = "https://gql.reddit.com"


TRUSTED_ORIGINS: Set[str] = {
    RESOURCE_BASE_URL,
    GRAPHQL_BASE_URL,
}


SENDBIRD_BASE_URL: str = "https://s.reddit.com"
SENDBIRD_APP_ID: str = "2515BDA8-9D3A-47CF-9325-330BC37ADA13"
