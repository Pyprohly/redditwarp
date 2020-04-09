
#
#  The
#    ______              _      _  _         _  _  _
#   |  ___  \           | |    | |(_)   _   | || || |
#   | |___) | _____   __| |  __| | _  _| |__| || || | _____   _____ ____
#   |  __  _/| ___ |/  _  |/  _  || |/_   _/| || || | \___ | / ___/|  _  \
#   | |  \ \ | ____|| (_| || (_| || |  | |__| || || |/ ___ || |    | |_) |
#   |_|   \_\|____/ \_____/\_____/|_|   \__/ \_____/ \_____/|_|    |  ___/
#                                                                  |_|
#                                                                 Library
#
#
#       #************************************************************
#       #mmmmmmmmmmmmmmmmmmmmNNNNNNmmmNNNNNNNmmmmmmmmmmmmmmmmmmmmmmmm*
#       #mmmmmmmmmmmmmmmNNNmmmmdddddddddddmmNNNNNmmmmmmmmmmmmmmmmmmmm*
#       #mmmmmmmmmmmmNNmmmddddddmmmmmNNNNNNh--yNmNNNmmmmmmmmmmmmmmmmm*
#       #mmmmmmmmmmNmmmddddmmmmmmmmmNNmmmmNd::hNmmmNNNmmmmmmmmmmmmmmm*
#       #mmmmmmmmNmmddddmmmmmmmmmmmmMmmmmmmmmmmmmmmmmNNNmmmmmmmmmmmmm*
#       #mmmmmmNNmmdddmmmmmmmmmmmmmmMmmmmmmmmmmmmmmmmmmNNmmmmmmmmmmmm*
#       #mmmmmNmmdddmmmmmmmmmmmNmhyso+///+sydNm+/yNmmmmmNNmmmmmmmmmmm*
#       #mmmmNmmdddmmmmmmNNNNho-``     `-.` `./yo.NmmmmmmNNmmmmmmmmmm*
#       #mmmNmmddmmmmmmm//my-` -+/`    :sso`   `+mNmmmmmmmNNmmmmmmmmm*
#       #mmNmmdddmmmmmNy.d/   `sss:    `+o/      mmmmmmmmmNNmmmmmmmmm*
#       #mNNmdddmmmmmmmNmy     .//`      `      .NmmmmmmmmmNNmmmmmmmm*
#       #mNmdddmmmmmmmmmNd         -+yhhho     :mNmmmmmmmmmNNmmmmmmmm*
#       #mNmdddmmmmmmmmmmNy-      `hmNmmh+  ./hNNNmmmmmmmmmNmmmmmmmmm*
#       #NNmdddmmmmmmmmmmmNmh+:..```.----:+smds+:--:+hNmmmNNmmmmmmmmm*
#       #NNmdddmmmmmmmmmmmNmmdddmyooooo+/:.`yo       :NmmmNNmmmmmmmmm*
#       #NNmdddmmmmmmmmmmdo:..`.y+          -m:---:ohmmmmNNmmmmmmmmmm*
#       #mNmdddmmmmmmmmmN-      +y           NNmmmmmmmmmNNmmmmmmmmmmm*
#       #mNmdddmmmmmmmmmmdyo+ooydN.          dmmmmmmmmmNNmmmmmmmmmmmm*
#       #mNNmdddmmmmmmmmmmmmmNNmmNy          mmmmmmmmNNmmmmmmmmmmmmmm*
#       #mmNmmddmmmmmmmmmmmmmmmmmmN+        .MmmmmmNNmmmmmmmmmmmmmmmm*
#       #mmmNmdddmmmmmmmmmmmmmmmmmmN+`      ydsydNmmmmmmmmmmmmmmmmmmm*
#       #mmmmNmdddmmmmmmmmmmmmmmmmyosy:```.sm//+sMmmmmmmmmmmmmmmmmmmm*
#       #mmmmmNmdddmmmmmmmmmmmmmNy/+odMddmmNNNNNmmmmmmmmmmmmmmmmmmmmm*
#       #mmmmmmNmmdddmmmmmmmmmmmmNNNmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*
#       #mmmmmmmNNmdddmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*
#       #mmmmmmmmmNNmdddmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*
#       ##############################################################
#
#
#
#############################################################################


from typing import NamedTuple

__all__ = (
	'__title__',
	'__summary__',
	'__uri__',
	'__version__',
	'__author__',
	'__license__',
	'__copyright__',
	'version_info',
)

class VersionInfo(NamedTuple):
	major: int
	minor: int
	micro: int
	releaselevel: str
	serial: int

version_info = VersionInfo(
	major=0,
	minor=1,
	micro=0,
	releaselevel='alpha',
	serial=0,
)

__title__ = 'RedditWarp'
__summary__ = 'The unofficial Reddit API wrapper for Python developers'
__uri__ = "https://github.com/Pyprohly/RedditWarp"

#__version__ = '.'.join(map(str, version_info[:3]))
__version__ = 'alpha'

__author__ = 'Pyprohly' # u/Pyprohly

__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Pyprohly'
