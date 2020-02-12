
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


def make_payload(payload, data, json):
	if payload is not None:
		return payload

	if data is not None:
		if isinstance(data, dict):
			return FormData(data)
		if isinstance(data, str):
			return Text(data)
		if isinstance(data, bytes):
			return Raw(data)
		raise NotImplementedError

	if json is not None:
		if isinstance(json, dict):
			return JSON(json)
		raise NotImplementedError

	return None
