

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
	"""HTTP 4XX family of errors.

	The request was badly formed or could not be fulfilled.
	"""

class BadRequest(ClientError):
	"""A 400 HTTP error occurred."""


class HTTPResponseErrorFactory:
	def __new__(self, response):
		...


class ServerError(ResponseError):
	"""HTTP 5XX family of errors.

	The server failed to fulfill an apparently valid request.
	"""

class NetworkError: pass
class BadRequest: pass
class TimeoutError: pass

class ContentCreationCooldown: pass

