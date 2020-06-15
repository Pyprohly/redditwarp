
from collections.abc import MutableMapping
import pickle

import pytest

from redditwarp.util.attribute_mapping_wrapper import AttributeMappingWrapper


def test_subclass():
	assert issubclass(AttributeMappingWrapper, MutableMapping)

def test_constructor():
	d = {}
	amw = AttributeMappingWrapper(d)
	assert abs(amw) is d

def test_getitem():
	amw = AttributeMappingWrapper({'a': 1, 'b': {'aa': 3}})
	assert amw['a'] == 1
	assert type(amw['b']) is dict
	assert amw['b']['aa'] == 3

	with pytest.raises(KeyError):
		amw['z']

def test_setitem():
	amw = AttributeMappingWrapper({'a': 1, 'b': 2})
	assert len(amw) == 2

	amw['c'] = 4
	assert amw['c'] == 4
	assert len(amw) == 3

	amw['d'] = {'dd': 4}
	assert type(amw['d']) is dict
	assert amw['d']['dd'] == 4

def test_delitem():
	amw = AttributeMappingWrapper({'a': 1, 'b': 2, 'c': 3})
	assert len(amw) == 3
	del amw['c']
	assert 'c' not in amw
	assert len(amw) == 2

def test_getattr():
	amw = AttributeMappingWrapper({'a': 1, 'b': {'bb': 22}})
	assert amw.a == 1

	assert type(amw.b) is AttributeMappingWrapper
	assert amw.b == {'bb': 22}
	assert amw.b.bb == 22

	with pytest.raises(AttributeError):
		amw.z
	with pytest.raises(AttributeError):
		amw['b'].bb

def test_setattr():
	amw = AttributeMappingWrapper({'a': 1, 'b': 2})
	assert len(amw) == 2
	amw.d = 4
	assert amw['d'] == 4
	assert len(amw) == 3

	amw.c = {'cc': 33}
	assert type(amw['c']) is dict
	assert type(amw.c) is AttributeMappingWrapper

def test_delattr():
	amw = AttributeMappingWrapper({'a': 1, 'b': 2, 'c': 3})
	assert len(amw) == 3
	del amw.c
	assert 'c' not in amw
	assert len(amw) == 2

def test_iter():
	assert set(AttributeMappingWrapper({'a': 1, 'b': 2, 'c': 3})) == {'a', 'b', 'c'}

def test_dir():
	amw = AttributeMappingWrapper({'a': 1, 'b': 2, 'c': 3})
	assert dir(amw) == sorted(amw)

def test_abs():
	d = {'key': 'value'}
	amw = AttributeMappingWrapper(d)
	d['key2'] = 'value2'
	assert 'key2' in amw
	assert amw['key2'] == 'value2'
	assert abs(amw) is d

def test_update():
	amw = AttributeMappingWrapper({'a': 1, 'b': 2, 'c': 3})
	assert len(amw) == 3
	amw.update({'c': 8, 'd': 11})
	assert len(amw) == 4
	assert amw['a'] == 1
	assert amw['b'] == 2
	assert amw['c'] == 8
	assert amw['d'] == 11

def test_clear():
	d = {'a': 1, 'b': 2, 'c': 3}
	amw = AttributeMappingWrapper(d)
	assert len(amw) == 3
	amw.clear()
	assert len(amw) == 0
	assert abs(amw) is d

def test_pickle():
	mydict = {
		'a': 1,
		'b': 2,
		'c': {'dee': 40, 'eee': {'eff': 'gee', 'aych': 80}},
		'foo': [1, 2, 3],
	}
	amw = AttributeMappingWrapper(mydict)
	for level in range(pickle.HIGHEST_PROTOCOL + 1):
		other = pickle.loads(pickle.dumps(amw, protocol=level))
		assert amw == other

def test_noclobber_mapping_methods():
	amw = AttributeMappingWrapper({})
	update_method = amw.update
	clear_method = amw.clear

	amw.update = 1
	assert amw['update'] == 1
	assert amw.update == update_method

	amw.update({'clear': 2})
	assert amw['clear'] == 2
	assert amw.clear == clear_method
