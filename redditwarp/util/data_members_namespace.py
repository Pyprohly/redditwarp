
import collections.abc
import inspect
from ast import literal_eval
import reprlib
from pprint import PrettyPrinter
from io import StringIO


rep = reprlib.Repr()
rep.maxlevel = 1
rep.maxstring = 250
rep.maxother = 250
reprepr = rep.repr

class _StrReprStr(str):
	def __repr__(self):
		return str(self)

def neat_repr_dict(d):
	return {
		k: (literal_eval(reprepr(v)) if isinstance(v, str) else _StrReprStr(reprepr(v)))
		for k, v in d.items()
	}


ppr = PrettyPrinter()
ppr_format = ppr._format

def pretty_format(obj):
	# This function ensures `obj`'s pretty-print-formatted string is
	# returned, since `pprint.pformat()` only invokes an object's
	# pretty printer if its __repr__ is long enough.
	sio = StringIO()
	ppr_format(obj, sio, 0, 999999, {}, 0)
	return sio.getvalue()


class DataMembersNamespace(collections.abc.Collection):
	def __init__(self, instance):
		self._instance = instance

	def __repr__(self):
		return f'<{self.__class__.__name__}({self._instance})>'

	def __str__(self):
		return pretty_format(self)

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
		leader = 'data members: '
		stream.write(leader)
		printer._format(
			neat_repr_dict(dict(obj._data_members())),
			stream,
			indent + len(leader),
			allowance,
			context,
			level,
		)

	if isinstance(getattr(PrettyPrinter, '_dispatch', None), dict):
		PrettyPrinter._dispatch[__repr__] = _pprint


class AttributeCollection(DataMembersNamespace):
	def __getitem__(self, key):
		try:
			value = getattr(self._instance, key)
		except AttributeError:
			raise KeyError(key)
		if inspect.ismethod(value):
			raise KeyError(key)
		return value
