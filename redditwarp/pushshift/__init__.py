"""A Pushshift API client.

Use this package as a scalpel. It's pagination based and doesn't do concurrency.

If you need to scrape lots of data, you'll be better using PMAW_.

.. _PMAW: https://github.com/mattpodolak/pmaw
"""

from . import core  # noqa: F401
from . import models  # noqa: F401
from . import paginators  # noqa: F401
