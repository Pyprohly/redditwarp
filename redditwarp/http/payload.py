
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
