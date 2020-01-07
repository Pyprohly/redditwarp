
from collections import namedtuple

version_info = namedtuple('VersionInfo', 'major minor micro releaselevel serial') \
(
	major=0,
	minor=1,
	micro=0,
	releaselevel='alpha',
	serial=0,
)

__title__ = 'RedditWarp'
__summary__ = 'Reddit API wrapper'
__uri__ = 'https://github.com/Pyprohly/RedditWarp'

__version__ = '.'.join(map(str, version_info[:3]))

__author__ = 'Pyprohly'
__email__ = 'pyprohly@outlook.com'

__license__ = 'MIT'
__copyright__ = 'Copyright 2020 ' + __author__
