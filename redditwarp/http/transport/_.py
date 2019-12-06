


class Response:
	def __init__(self, status, headers, data):
		self.status = status
		self.headers = headers
		self.data = data

	def json(self):
		...
