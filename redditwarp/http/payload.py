
from typing import Optional, Any, Dict

class Payload:
	CONTENT_TYPE_SUGGESTION = ''

class Raw(Payload):
	CONTENT_TYPE_SUGGESTION = 'application/octet-stream'
	def __init__(self, data: bytes):
		self.data = data

class FormData(Payload):
	CONTENT_TYPE_SUGGESTION = 'application/x-www-form-urlencoded'
	def __init__(self, data: Dict[str, str]):
		self.data = data

class MultiPart(Payload):
	CONTENT_TYPE_SUGGESTION = 'multipart/form-data'
	def __init__(self, data: Any):
		self.data = data

class Text(Payload):
	CONTENT_TYPE_SUGGESTION = 'text/plain'
	def __init__(self, text: str):
		self.text = text

class JSON(Payload):
	CONTENT_TYPE_SUGGESTION = 'application/json'
	def __init__(self, json: Any):
		self.json = json


def make_payload(payload: Optional[Payload], data: Any, json: Any):
	if payload is not None:
		return payload

	if data is not None:
		if isinstance(data, dict):
			d = {k: str(v) for k, v in data.items()}
			data.clear()
			return FormData(d)
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
