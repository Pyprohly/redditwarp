#!/usr/bin/env python3
"""
Exchange an authorization code for an access/refresh token.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from types import FrameType

###
import argparse
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
add = parser.add_argument
add('client_id', nargs='?')
add('client_secret', nargs='?')
add('authorization_code', nargs='?')
add('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
add('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
add('--authorization-code', metavar='CLIENT_SECRET', dest='authorization_code_opt', help=argparse.SUPPRESS)
add('--redirect-uri', default="http://localhost:8080", help="\N{ZERO WIDTH SPACE}")
args = parser.parse_args()
###;

import sys
import os
import signal
from functools import partial
from pprint import pp

import redditwarp
from redditwarp.http.transport.SYNC import load_transport, new_session
from redditwarp.core.SYNC import RedditTokenObtainmentClient
from redditwarp.core.user_agent_SYNC import get_user_agent_from_session

def get_client_cred_input(prompt: str, env: str, v: Optional[str]) -> str:
    if v is None:
        v = input(prompt)
    if v == '.':
        v = os.environ[env]
        print(v)
    return v

def get_client_id(args: argparse.Namespace) -> str:
    v = args.client_id_opt or args.client_id
    return get_client_cred_input('Client ID: ', 'redditwarp_client_id', v)

def get_client_secret(args: argparse.Namespace) -> str:
    v = args.client_secret_opt or args.client_secret
    return get_client_cred_input('Client secret: ', 'redditwarp_client_secret', v)

if not sys.flags.interactive:
    @partial(signal.signal, signal.SIGINT)
    def _(sig: int, frame: Optional[FrameType]) -> None:
        print('KeyboardInterrupt', file=sys.stderr)
        sys.exit(130)

load_transport()

client_id = get_client_id(args)
client_secret = get_client_secret(args)
code: str = args.authorization_code_opt or args.authorization_code or input('Code: ')
redirect_uri: str = args.redirect_uri

print('* Step 3. Exchange the authorization code for an access/refresh token.\n')

grant = redditwarp.auth.grants.AuthorizationCodeGrant(code, redirect_uri)
print('Authorization grant:')
pp(dict(grant))
print()

session = new_session()
ua = get_user_agent_from_session(session) + " redditwarp.cli.exchange_authorization_code"
token_client = RedditTokenObtainmentClient(
    session,
    redditwarp.auth.const.TOKEN_OBTAINMENT_URL,
    (client_id, client_secret),
    grant,
    headers={'User-Agent': ua},
)

print('Obtaining token(s) from token server...\n')

token = token_client.fetch_token()

print(f'''\
     Access token: {token.access_token}
    Refresh token: {token.refresh_token}''')
