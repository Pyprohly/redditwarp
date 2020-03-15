"""Artifical class constructs that roughly reflect the design model of some Reddit objects."""

class ThingMixin:
	THING_PREFIX = 't'

	def __init__(self, data):
		super().__init__(data)
		id_ = data['id']
		self.id = int(id_, 36)
		self.id36 = id_
		self.full_id36 = f'{self.THING_PREFIX}_{id_}'

	def __repr__(self):
		return f'<{self.__class__.__name__} id36={self.id36!r}>'
