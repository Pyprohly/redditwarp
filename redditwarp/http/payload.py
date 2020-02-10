
from typing import Any

class Payload:
	pass

class Raw(Payload):
	def __init__(self, data: bytes):
		self.data = data

class FormData(Payload):
	def __init__(self, data: Any):
		self.data = data

class MultiPart(Payload):
	def __init__(self, data: Any):
		self.data = data

class Text(Payload):
	def __init__(self, text: str):
		self.text = text

class JSON(Payload):
	def __init__(self, json: Any):
		self.json = json


def make_payload(data):
	if data is None:
		return None

	if isinstance(data, dict):
		return FormData(data)
	if isinstance(data, str):
		return Text(data)

	raise NotImplementedError
