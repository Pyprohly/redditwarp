#!/usr/bin/env python
"""
Revoke an access or refresh token.

If neither -a nor -r is specified then the token server will automatically
determine the token type, as per RFC 7009 Section 2.1.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from types import FrameType

###
import argparse
class Formatter(argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
group = parser.add_mutually_exclusive_group()
group.add_argument('-a', action='store_true', help="hint to the server that the token is an access token")
group.add_argument('-r', action='store_true', help="hint to the server that the token is a refresh token")
parser.add_argument('client_id', nargs='?')
parser.add_argument('client_secret', nargs='?')
parser.add_argument('token', nargs='?')
parser.add_argument('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
parser.add_argument('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
args = parser.parse_args()
###;

import sys
import os
import signal
from functools import partial

import redditwarp
from redditwarp.http.transport.reg_SYNC import get_transport_adapter_module
from redditwarp.http.transport.auto_SYNC import new_connector
from redditwarp.http.misc_handlers.apply_params_and_headers_SYNC import ApplyDefaultHeaders
from redditwarp.http.http_client_SYNC import HTTPClient
from redditwarp.auth.SYNC import TokenRevocationClient
from redditwarp.core.ua_SYNC import get_suitable_user_agent

def get_client_cred_input(v: Optional[str], prompt: str, env: str) -> str:
    if v is None:
        v = input(prompt)
    if v == '.':
        v = os.environ[env]
        print(v)
    return v

if not sys.flags.interactive:
    @partial(signal.signal, signal.SIGINT)
    def _(sig: int, frame: Optional[FrameType]) -> None:
        print('KeyboardInterrupt', file=sys.stderr)
        sys.exit(130)

# Raise here if no HTTP transport module is installed.
get_transport_adapter_module()

client_id = get_client_cred_input(
        (args.client_id_opt or args.client_id),
        'Client ID: ', 'redditwarp_client_id')
client_secret = get_client_cred_input(
        (args.client_secret_opt or args.client_secret),
        'Client secret: ', 'redditwarp_client_secret')
token: str = args.token or input('Token: ')
access_token_needs_revoking: bool = args.a
refresh_token_needs_revoking: bool = args.r

connector = new_connector()
ua = get_suitable_user_agent(connector.__module__) + " redditwarp.cli.revoke_token"
headers = {'User-Agent': ua}
revoke_token_client = TokenRevocationClient(
    HTTPClient(ApplyDefaultHeaders(connector, headers)),
    redditwarp.core.const.TOKEN_REVOCATION_URL,
    (client_id, client_secret),
)

if access_token_needs_revoking == refresh_token_needs_revoking:
    revoke_token_client.revoke_token(token)
elif access_token_needs_revoking:
    revoke_token_client.revoke_access_token(token)
else:
    revoke_token_client.revoke_refresh_token(token)
