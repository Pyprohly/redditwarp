
from typing import ClassVar, Optional
from dataclasses import dataclass

@dataclass
class AuthorizationGrant:
	"""An authorization grant is a credential representing the resource
	owner's authorization that's used to exchange for an access token.

	An empty string should be treated the same as `None` in all fields that
	are annotated as `Optional`.
	"""
	grant_type: ClassVar[str] = ''

@dataclass
class AuthorizationCodeGrant(AuthorizationGrant):
	grant_type = 'authorization_code'
	code: str
	redirect_uri: Optional[str]
	client_id: Optional[str] = None

@dataclass
class ResourceOwnerPasswordCredentialsGrant(AuthorizationGrant):
	grant_type = 'password'
	username: str
	password: str
	scope: Optional[str] = None

@dataclass
class ClientCredentialsGrant(AuthorizationGrant):
	grant_type = 'client_credentials'
	scope: Optional[str] = None

@dataclass
class RefreshTokenGrant(AuthorizationGrant):
	grant_type = 'refresh_token'
	refresh_token: str
	scope: Optional[str] = None

@dataclass
class InstalledClientGrant(AuthorizationGrant):
	# A reddit-specific extension grant.
	grant_type = 'https://oauth.reddit.com/grants/installed_client'
	device_id: str
	scope: Optional[str] = None


###


@dataclass
class _AuthorizationGrantRequest:
	"""Used in the initital request part of the Authorization Code
	and Implicit flows.

	Authorization Code flow: a request must be made before the
	authorization grant can be constructed.

	Implicit flow: the initial request immediately returns an
	access token.
	"""
	response_type: ClassVar[str] = ''
	client_id: str
	redirect_uri: Optional[str]
	scope: Optional[str]
	state: Optional[str]

class AuthorizationCodeGrantRequest(_AuthorizationGrantRequest):
	response_type = 'code'

class ImplicitGrantRequest(_AuthorizationGrantRequest):
	response_type = 'token'
