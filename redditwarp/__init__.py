
from .__about__ import __version__  # noqa
from .client import *  # noqa

root_name, _, _ = __name__.partition('.')
globals()[root_name] = __import__(root_name)
