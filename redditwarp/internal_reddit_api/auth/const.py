
from typing import Any

# Although the authorisation system used by Reddit's internal API is not
# OAuth2-spec compliant, there are similarities in the way credentials are used.

REDDIT_MOBILE_ANDROID_CLIENT_ID: str = 'ohXpoqrZYub1kg'
REDDIT_MOBILE_IOS_CLIENT_ID: str = 'LNDo9k1o8UAEUw'

ACCOUNTS_BASE_URL: str = "https://accounts.reddit.com"
TOKEN_OBTAINMENT_ENDPOINT_PATH: str = "/api/access_token"
TOKEN_OBTAINMENT_URL: str = ACCOUNTS_BASE_URL + TOKEN_OBTAINMENT_ENDPOINT_PATH

GRANT_DATA: Any = {"scopes":["*","email","pii"]}


GRAPHQL_BASE_URL: str = "https://gql.reddit.com"


SENDBIRD_BASE_URL: str = "https://s.reddit.com"
SENDBIRD_APP_ID: str = "2515BDA8-9D3A-47CF-9325-330BC37ADA13"
