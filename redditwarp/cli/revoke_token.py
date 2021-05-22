#!/usr/bin/env python3
"""
Revoke an access or refresh token.

If neither -a nor -r is specified then the token server will automatically
determine the token type.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from types import FrameType

import argparse
class Formatter(argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
group = parser.add_mutually_exclusive_group()
group.add_argument('-a', action='store_true', help='hint to the server the token is an access token')
group.add_argument('-r', action='store_true', help='hint to the server the token is a refresh token')
parser.add_argument('client_id', nargs='?')
parser.add_argument('client_secret', nargs='?')
parser.add_argument('token', nargs='?')
parser.add_argument('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
parser.add_argument('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
args = parser.parse_args()

import sys
import os
import signal

import redditwarp
from redditwarp.http.transport.SYNC import (
    load_transport_module,
    new_session,
    get_session_underlying_library_name_and_version,
)
from redditwarp.auth.SYNC import TokenRevocationClient
from redditwarp.http.components.apply_params_and_headers_SYNC import ApplyDefaultParamsAndHeaders

def get_client_cred_input(prompt: str, env: str, v: Optional[str]) -> str:
    if v is None:
        v = input(prompt)
    if v == '.':
        v = os.environ[env]
        print(v)
    return v

def get_client_id(v: Optional[str]) -> str:
    return get_client_cred_input('Client ID: ', 'redditwarp_client_id', v)

def get_client_secret(v: Optional[str]) -> str:
    return get_client_cred_input('Client secret: ', 'redditwarp_client_secret', v)

def handle_sigint(sig: int, frame: FrameType) -> None:
    print('KeyboardInterrupt', file=sys.stderr)
    sys.exit(130)

signal.signal(signal.SIGINT, handle_sigint)

load_transport_module()

client_id = get_client_id(args.client_id_opt or args.client_id)
client_secret = get_client_secret(args.client_secret_opt or args.client_secret)
token: str = args.token or input('Token: ')
access_token_needs_revoking: bool = args.a
refresh_token_needs_revoking: bool = args.r

session = new_session()
transport_name, transport_version = get_session_underlying_library_name_and_version(session)
user_agent = (
    f"RedditWarp/{redditwarp.__version__} "
    f"{transport_name}/{transport_version} "
    "redditwarp.cli.revoke_token"
)
headers = {'User-Agent': user_agent}
requestor = ApplyDefaultParamsAndHeaders(session, headers=headers)
revoke_token_client = TokenRevocationClient(
    requestor,
    redditwarp.auth.const.TOKEN_REVOCATION_URL,
    (client_id, client_secret),
)

if access_token_needs_revoking == refresh_token_needs_revoking:
    revoke_token_client.revoke_token(token)
elif access_token_needs_revoking:
    revoke_token_client.revoke_access_token(token)
else:
    revoke_token_client.revoke_refresh_token(token)
