
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional

from typing import ClassVar
from dataclasses import dataclass

__all__ = (
	'AuthorizationGrant',
	'AuthorizationCodeGrant',
	'ResourceOwnerPasswordCredentialsGrant',
	'ClientCredentialsGrant',
	'RefreshTokenGrant',
	'InstalledClientGrant',
	'auto_grant_factory',
)

@dataclass
class AuthorizationGrant:
	"""An authorization grant is a credential representing the resource
	owner's authorization that's used to exchange for a bearer token.

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
	grant_type = "https://oauth.reddit.com/grants/installed_client"
	device_id: str
	scope: Optional[str] = None


def auto_grant_factory(
	refresh_token: Optional[str],
	username: Optional[str],
	password: Optional[str],
) -> Optional[AuthorizationGrant]:
	"""Produce a simple, non-expiring grant from the given credentials.

		* Refresh Token
		* Resource Owner Password Credentials
		* Client Credentials

	Note this function won't return the (Reddit-specific) Installed Client
	grant type. This grant should be explicitly created if needed.
	"""
	if refresh_token:
		return RefreshTokenGrant(refresh_token)
	if username and password:
		return ResourceOwnerPasswordCredentialsGrant(username, password)
	return ClientCredentialsGrant()
