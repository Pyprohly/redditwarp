
from datetime import datetime, timezone
from .object import FunBox
from .design_classes import ThingMixin

class Submission(ThingMixin, FunBox):
	THING_PREFIX = 't3'

	def __init__(self, data):
		super().__init__(data)
		self.created_at = datetime.fromtimestamp(data['created_utc'], timezone.utc)
		self.created_ut = int(data['created_utc'])

class TextPost(Submission):
	def __init__(self, data):
		super().__init__(data)
		self.body = data['selftext']
		self.body_html = data['selftext_html']

class LinkPost(Submission):
	pass
