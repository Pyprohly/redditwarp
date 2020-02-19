
import collections.abc
import inspect
import reprlib
from ast import literal_eval
from pprint import PrettyPrinter, pformat

rep = reprlib.Repr()
rep.maxlevel = 1
rep.maxstring = 250
rep.maxother = 250
reprepr = rep.repr

class _StrReprStr(str):
	def __repr__(self):
		return str(self)

def neat_repr_dict(d):
	return {k: (literal_eval(reprepr(v)) if isinstance(v, str) else _StrReprStr(reprepr(v))) for k, v in d.items()}

class DataMembersNamespace(collections.abc.Collection):
	def __init__(self, instance):
		self._instance = instance

	def __repr__(self):
		return f'data members: %r' % neat_repr_dict(dict(self._data_members()))

	def __iter__(self):
		return (k for k, v in self._data_members())

	def __len__(self):
		return sum(1 for _ in self._data_members())

	def __contains__(self, item):
		try:
			value = getattr(self._instance, item)
		except AttributeError:
			return False
		return not inspect.ismethod(value)

	def __getattr__(self, name):
		value = getattr(self._instance, name)
		if inspect.ismethod(value):
			raise AttributeError(f'{self._instance.__class__.__name__!r} has no data attribute {name!r}')
		return value

	def __dir__(self):
		return list(self)

	def _data_members(self):
		for name, value in inspect.getmembers(self._instance, (lambda x: not inspect.ismethod(x))):
			if value is self:
				continue
			if name.startswith('_'):
				continue
			yield name, value

	def _pprint(printer, obj, stream, indent, allowance, context, level):
		stream.write('data members: ')
		printer._format(
			neat_repr_dict(dict(obj._data_members())),
			stream,
			indent + len('data members: '),
			allowance + 1,
			context,
			level,
		)

	if isinstance(getattr(PrettyPrinter, '_dispatch', None), dict):
		PrettyPrinter._dispatch[__repr__] = _pprint


class AttributeCollection(DataMembersNamespace):
	def __str__(self):
		return pformat(self)

	def __getitem__(self, key):
		try:
			value = getattr(self._instance, key)
		except AttributeError:
			raise KeyError(key)
		if inspect.ismethod(value):
			raise KeyError(key)
		return value
