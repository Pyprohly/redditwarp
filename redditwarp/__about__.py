
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
#       #....................````````````````........................*
#       #...............```....------------.`````....................*
#       #............``...------.....``````:dd/`.```.................*
#       #..........`...----.........` ....`-hh:`...```...............*
#       #........`..----............ ................```.............*
#       #......``..---.............. ..................``............*
#       #.....`..---...........`.:/+osyyys+/-`.sy`......``...........*
#       #....`..---......````:odNNMMMMMNdmNMNmy/om`......``..........*
#       #...`..--.......yy./dNMdsyNMMMMh++oNMMMNs.`.......``.........*
#       #..`..---.....`/mmyMMMN+++hMMMMNsoyMMMMMM.........``.........*
#       #.``.---.......`./MMMMMmyyNMMMMMMNMMMMMMm`.........``........*
#       #.`.---.........`-MMMMMMMMds/::::sNMMMMh.`.........``........*
#       #.`.---..........`/dMMMMMMN:.`..:sMMmy:```.........``........*
#       #``.---...........`.:shmmNNNmddddhss+.-shddhs:`...``.........*
#       #``.---...........`..---./ooooosyhmN/oMMMMMMMh`...``.........*
#       #``.---..........-ohmmNm/sMMMMMMMMMMd.hdddho:....``..........*
#       #.`.---.........`dMMMMMMs/MMMMMMMMMMM``.........``...........*
#       #.`.---..........-/snoo/-`mMMMMMMMMMM-.........``............*
#       #.``.---.............``..`/MMMMMMMMMM........``..............*
#       #..`..--..................`sMMMMMMMMm .. ...``...............*
#       #...`.---..................`sNMMMMMM/-+/-`...................*
#       #....`.---................/o+/hNNNm+.yys+ ...................*
#       #.....`.---.............`/yso- .....`````....................*
#       #......`..---............```.................................*
#       #.......``.---...............................................*
#       #.........``.---.............................................*
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
