
from .__about__ import __version__  # noqa
from .util.module_importing import lazy_import  # noqa
from .client import *  # noqa

globals()[__name__] = __import__(__name__)
