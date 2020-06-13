
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .design_classes import Thing

class Submission(Thing):
	class AuthorComponent:
		...

	THING_PREFIX = 't3'

	def __init__(self, d: Mapping[str, Any]) -> None:
		super().__init__(d)
		self.created_ut = int(d['created_utc'])
		self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
		self.permalink: str = d['url']
		self.relative_permalink: str = d['permalink']
		self.title: str = d['title']
		self.score: int = d['score']

		# DELETE THIS. Create self.subreddit object instead
		#self.subreddit_name = d['subreddit']
		#_, _, self.subreddit_id36 = d['subreddit'].partition('_')
		#self.subreddit_id = int(self.subreddit_id36, 36)




class TextPost(Submission):
	def __init__(self, d: Mapping[str, Any]) -> None:
		super().__init__(d)
		self.body = d['selftext']
		self.body_html = d['selftext_html']

class LinkPost(Submission):
	pass
