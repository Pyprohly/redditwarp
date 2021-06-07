#!/usr/bin/env python3
"""
Run refresh_token.py with the `--access-token-only` flag.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from types import FrameType

import argparse
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
add = parser.add_argument
add('client_id', nargs='?')
add('client_secret', nargs='?')
add('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
add('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
add('--scope', default='*', help='an OAuth2 scope string')
add('--redirect-uri', default='http://localhost:8080', help='\N{ZERO WIDTH SPACE}')
add('--no-web-browser', action='store_true', help="don't launch a browser")
add('--web-browser-name', help="the web browser to open")
parser.parse_args()

import sys
import os.path as op
import subprocess
import signal

import redditwarp

def handle_sigint(sig: int, frame: FrameType) -> None:
    sys.exit(130)

signal.signal(signal.SIGINT, handle_sigint)

script = op.dirname(redditwarp.__file__) + '/cli/refresh_token.py'

subprocess.run([sys.executable, script, '--access-token-only'] + sys.argv[1:])
