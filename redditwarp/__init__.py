
__all__ = '*'

from . import SYNC, ASYNC  # noqa: F401
from .__about__ import (  # noqa: F401
    __title__ as __title__,
    __summary__ as __summary__,
    __uri__ as __uri__,
    __url__ as __url__,
    __version__ as __version__,
    version_info as version_info,
    __version_info__ as __version_info__,
    __author__ as __author__,
    __license__ as __license__,
    __copyright__ as __copyright__,
)

globals()[__name__] = __import__(__name__)
