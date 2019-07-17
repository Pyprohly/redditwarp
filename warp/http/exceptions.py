

class HTTPException(Exception):
	pass

class TransmissionError(HTTPException):
	"""An error occurred during an HTTP transmission.

	The request failed to complete.
	"""



class ResponseError(HTTPException):
	"""The request completed but the response indicated an error."""
	def __init__(self, response):
		self.response = response

class ClientError(ResponseError):
	"""HTTP 4XX family of errors."""
class BadRequest(ClientError):
	"""A 400 HTTP error occurred."""



class ServerError(ResponseError):
	"""HTTP 5XX family of errors.

	The server failed to fulfill an apparently valid request.
	"""



class AuthError(HTTPException):
	"""Error class for authentication-related errors."""

class InvalidToken(AuthError):
	pass

class RefreshError(AuthError):
	"""Refreshing the credential's access token failed."""
