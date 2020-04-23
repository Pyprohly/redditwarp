
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

@dataclass(frozen=True)
class AuthorizationGrant:
	"""An authorization grant is a credential representing the resource
	owner's authorization that's used to exchange for a bearer token.

	An empty string should be treated the same as `None` in all fields
	annotated as `Optional`. The annotation is a reflection of the field
	value requirements of various grants types defined in the OAuth2 spec.
	"""
	GRANT_TYPE: ClassVar[str] = ''

@dataclass(frozen=True)
class AuthorizationCodeGrant(AuthorizationGrant):
	GRANT_TYPE = 'authorization_code'
	code: str
	redirect_uri: Optional[str]
	client_id: Optional[str] = None

@dataclass(frozen=True)
class ResourceOwnerPasswordCredentialsGrant(AuthorizationGrant):
	GRANT_TYPE = 'password'
	username: str
	password: str
	scope: Optional[str] = None

@dataclass(frozen=True)
class ClientCredentialsGrant(AuthorizationGrant):
	GRANT_TYPE = 'client_credentials'
	scope: Optional[str] = None

@dataclass(frozen=True)
class RefreshTokenGrant(AuthorizationGrant):
	GRANT_TYPE = 'refresh_token'
	refresh_token: str
	scope: Optional[str] = None

@dataclass(frozen=True)
class InstalledClientGrant(AuthorizationGrant):
	GRANT_TYPE = "https://oauth.reddit.com/grants/installed_client"
	device_id: str
	scope: Optional[str] = None


def auto_grant_factory(
	refresh_token: Optional[str],
	username: Optional[str],
	password: Optional[str],
) -> Optional[AuthorizationGrant]:
	"""Produce a simple non-expiring grant from the provided credentials:

		* Refresh Token
		* Resource Owner Password Credentials
		* Client Credentials

	This function doesn't return the (Reddit-specific) Installed Client
	grant type.
	"""
	if refresh_token:
		return RefreshTokenGrant(refresh_token)
	if username and password:
		return ResourceOwnerPasswordCredentialsGrant(username, password)
	if username or password:
		return None
	return ClientCredentialsGrant()
