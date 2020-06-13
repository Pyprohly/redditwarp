'''
import pytest

import sys, os
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
import client
del sys.path[1]

@pytest.fixture(scope='session')
def userless_client():
	return client.userless_client

@pytest.fixture(scope='session')
def user_client():
	return client.user_client
'''
