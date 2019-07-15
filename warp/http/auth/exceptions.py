"""Authentication related exceptions."""


class AuthError(Exception):
	"""Base class for all authentication-related errors."""

class TransportError(AuthError):
	"""An error occurred during an HTTP request."""

class RefreshError(AuthError):
	"""Refreshing the credential's access token failed."""
