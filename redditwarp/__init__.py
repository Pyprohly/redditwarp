"""An API wrapper for the Reddit API."""

__all__ = '*'

from . import __about__  # noqa: F401
from .__about__ import (  # noqa: F401
    __title__ as __title__,
    __summary__ as __summary__,
    __uri__ as __uri__,
    __version__ as __version__,
    __author__ as __author__,
    __license__ as __license__,
    __copyright__ as __copyright__,
)
from . import auth  # noqa: F401
from . import core  # noqa: F401
from . import http  # noqa: F401
from . import websocket  # noqa: F401
from . import iterators  # noqa: F401
from . import pagination  # noqa: F401
from . import models  # noqa: F401
from . import dtos  # noqa: F401
from . import model_loaders  # noqa: F401
from . import util  # noqa: F401
from . import exceptions  # noqa: F401
from . import types  # noqa: F401



import sys as _sys

globals()[__name__] = __import__(__name__)

from . import _cli
_sys.modules[__name__ + '.cli'] = _cli
