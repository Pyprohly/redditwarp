
import os
import pytest
from redditwarp.util.data_members_namespace import DataMembersNamespace, AttributeCollection

class A:
	def __init__(self):
		self.aaa = 1

	@property
	def bbb(self):
		return 2

	def ccc(self):
		return 3

class B(A):
	pass

class C(B):
	def __init__(self):
		super().__init__()
		self.ddd = 4
		self.eee = lambda: 5


class TestDataAttributeNamespace:
	def test_getattr(self):
		d = DataMembersNamespace(C())
		assert d.aaa == 1
		assert d.bbb == 2
		assert d.ddd == 4
		assert d.eee() == 5

		with pytest.raises(AttributeError):
			d.ccc

		with pytest.raises(AttributeError):
			d.zzz

	def test_iter(self):
		assert list(DataMembersNamespace(C())) == ['aaa', 'bbb', 'ddd', 'eee']

	def test_len(self):
		assert len(DataMembersNamespace(C())) == 4

	def test_contains(self):
		d = DataMembersNamespace(C())
		assert 'aaa' in d
		assert 'bbb' in d
		assert 'ccc' not in d
		assert 'ddd' in d
		assert 'eee' in d

	def test_dir(self):
		d = DataMembersNamespace(C())
		assert dir(d) == ['aaa', 'bbb', 'ddd', 'eee']

	def test_print(self):
		# Check no exception raised
		with open(os.devnull, 'w') as null:
			print(DataMembersNamespace(C()), file=null)

class TestAttributeCollection:
	def test_general(self):
		assert issubclass(AttributeCollection, DataMembersNamespace)

	def test_getitem(self):
		d = AttributeCollection(C())
		assert d['aaa'] == 1
		assert d['bbb'] == 2
		assert d['ddd'] == 4
		assert d['eee']() == 5

		with pytest.raises(KeyError):
			d['ccc']

		with pytest.raises(KeyError):
			d['zzz']
