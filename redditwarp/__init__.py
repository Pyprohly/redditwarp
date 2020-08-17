
from .__about__ import __version__  # noqa
from .client import *  # noqa

globals()[__name__] = __import__(__name__)
