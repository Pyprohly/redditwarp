
import os
import time

import redditwarp
from redditwarp.auth import ClientCredentials, ClientCredentialsGrant, RefreshTokenGrant
from redditwarp.http import HTTPClient
from redditwarp.http.transport.requests import new_session
from redditwarp.auth.client_sync import TokenClient
from redditwarp.auth import TOKEN_ENDPOINT
from redditwarp.http.authorizer_sync import Authorizer, Authorized
from redditwarp.http.ratelimiter_sync import RateLimited

client_credentials = ClientCredentials(
	os.environ['redditwarp_client_id'],
	os.environ['redditwarp_client_secret'],
)
session = new_session()
# Disable response compression.
#session.headers['Accept-Encoding'] = 'identity'

authorizer = Authorizer(
	TokenClient(
		session,
		TOKEN_ENDPOINT,
		client_credentials,
		ClientCredentialsGrant(),
	),
	None,
)
requestor = RateLimited(Authorized(session, authorizer))
userless_http = HTTPClient(
	requestor,
	session,
	authorizer,
)
userless_client = redditwarp.Client.from_http(userless_http)
authorizer.token = redditwarp.auth.token.Token('<ACCESS_TOKEN>')

authorizer = Authorizer(
	TokenClient(
		session,
		TOKEN_ENDPOINT,
		client_credentials,
		RefreshTokenGrant(os.environ['redditwarp_refresh_token']),
	),
	None,
)
requestor = RateLimited(Authorized(session, authorizer))
user_http = HTTPClient(
	requestor,
	session,
	authorizer,
)
user_client = redditwarp.Client.from_http(user_http)
authorizer.token = redditwarp.auth.token.Token('<ACCESS_TOKEN>')
