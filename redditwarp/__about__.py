
#
#  The
#    ______              _      _  _         _  _  _
#   |  ___  \           | |    | |(_)   _   | || || |
#   | |___) | _____   __| |  __| | _  _| |__| || || | _____   _____ ____
#   |  __  _/| ___ |/  _  |/  _  || |/_   _/| || || | \___ | / ___/|  _  \
#   | |  \ \ | ____|| (_| || (_| || |  | |__| || || |/ ___ || |    | |_) |
#   |_|   \_\|____/ \_____|\_____||_|   \__/ \_____/ \_____||_|    |  ___/
#                                                                  |_|
#                                                                 Library
#
#
#       #************************************************************
#       #....................````````````````........................*
#       #...............```....------------.`````....................*
#       #............``...------.....``````:dd-`````.................*
#       #..........`...----.........` ....`-hh:`...```...............*
#       #........`..----............ ................```.............*
#       #......``..---.............. ..................``............*
#       #.....`..---...........`.:/+osyyys+/-`.sy`......``...........*
#       #....`..---.......-``:odNNMMMMMNdmNMNmy/om`......``..........*
#       #...`..--......`yd-/dNMdsyNMMMMh++dNMMMNs.`.......``.........*
#       #..`..---.....`/m.yMMMN+++hMMMMNsoyMMMMMM.........``.........*
#       #.``.---.......`./MMMMMmyyNMMMMMMNMMMMMMm`.........``........*
#       #.`.---.........`-MMMMMMMMds/::::sNMMMMh.`.........``........*
#       #.`.---..........`/dMMMMMMN:.`..:sMMNmy:``.........``........*
#       #``.---...........`.:shmmNNNmddddhss+.-shddhs:`...``.........*
#       #``.---..............---./ooooosyhmo/oNMMMMMMh`...``.........*
#       #``.---..........-ohmmNm/sMMMMMMMMMMd.hdddhoP....``..........*
#       #.`.---.........`dMMMMMMs/MMMMMMMMMMM``.........``...........*
#       #.`.---..........-/snoo/-`mMMMMMMMMMM-.........``............*
#       #.``.---.............``..`/MMMMMMMMMM........``..............*
#       #..`..--..................`sMMMMMMMMm `` ...``...............*
#       #...`.---..................`sNMMMMMM/-+/-`...................*
#       #....`.---................/o-/hNNNN+-yys+ ...................*
#       #.....`.---.............`/yso- .....`````....................*
#       #......`..---............```.................................*
#       #.......``.---...............................................*
#       #.........``.---.............................................*
#       ##############################################################
#
#
#
#############################################################################

from __future__ import annotations

version_major: int = 1
version_minor: int = 1
version_micro: int = 0
version_extra: str = '.post.dev'

version_patch: int = version_micro
version_triad: tuple[int, int, int] = (version_major, version_minor, version_micro)
version_string: str = '.'.join(map(str, version_triad)) + version_extra

__version__: str = version_string

__title__: str = 'RedditWarp'
__summary__: str = "The unofficial Reddit API library for Python."
__uri__: str = "https://github.com/Pyprohly/redditwarp"
__url__: str = __uri__
__author__: str = 'Pyprohly'
__email__: str = 'pyprohly@gmail.com'
__license__: str = 'MIT'
__copyright__: str = 'Copyright 2023 Pyprohly'
