#!/usr/bin/env python3
"""
Step through the OAuth2 Authorization Code flow to obtain bearer tokens.

If your refresh token or access token is ever compromised then just
fetch new tokens with this tool to invalidated the old tokens.
"""

from __future__ import annotations
from typing import Optional, Any

import argparse
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
add = parser.add_argument
add('client_id', nargs='?')
add('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
add('client_secret', nargs='?')
add('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
add('--scope', default='*', help='an OAuth2 scope string')
add('--redirect-uri', default='http://localhost')
add('--duration', choices=['temporary', 'permanent'], default='permanent', help=argparse.SUPPRESS)
add('--no-web-browser', action='store_true')
args = parser.parse_args()

import sys
import os
import re
import uuid
import socket
import urllib.parse
import webbrowser
import signal

import redditwarp

def get_client_cred_input(prompt: str, env: str, v: Optional[str]) -> str:
    if v is None:
        v = input(prompt)
    if v in '.,':
        v = os.environ[env]
        if v == '.':
            print(v)
    return v

def get_client_id(v: Optional[str]) -> str:
    return get_client_cred_input('Client ID: ', 'redditwarp_client_id', v)

def get_client_secret(v: Optional[str]) -> str:
    return get_client_cred_input('Client secret: ', 'redditwarp_client_secret', v)

def signal_handler(signal: int, frame: Any) -> None:
    print('KeyboardInterrupt', file=sys.stderr)
    raise SystemExit(1)

signal.signal(signal.SIGINT, signal_handler)

transporter = redditwarp.http.transport.get_default_sync_transporter()
if transporter is None:
    raise ModuleNotFoundError('An HTTP transport library needs to be installed.')
new_session = transporter.module.new_session  # type: ignore[attr-defined]

client_id = get_client_id(args.client_id_opt or args.client_id)
client_secret = get_client_secret(args.client_secret_opt or args.client_secret)
scope: str = args.scope
redirect_uri: str = args.redirect_uri
duration: str = args.duration
no_web_browser: bool = args.no_web_browser
state = str(uuid.uuid4())

print('~=~ Reddit OAuth2 Authorization Code flow ~=~\n')
print('Step 1. Build the authorization URL and direct the user to the authorization server.\n')

params = {
    'response_type': 'code',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scope,
    'state': state,
    'duration': duration,
}
url = f"{redditwarp.auth.const.AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
print(url)
print()

if not no_web_browser:
    webbrowser.open(url)

print('Step 2. Wait for the authorization server response and extract the authorization code.')

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 8080))
    server.listen(1)
    client, addr = server.accept()
print()
print(addr)
with client:
    data = client.recv(8192)
    client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

decoded = data.strip().decode()
print(f"@```\n{decoded}\n```@\n")
match = re.match(r"^GET /\?([^ ]*) HTTP", decoded)
if not match:
    raise Exception
query = match[1]
d = urllib.parse.parse_qs(query)
response_params = {k: v[0] for k, v in d.items()}

received_state = response_params['state']
if received_state != state:
    raise Exception(f'sent state ({state}) did not match received ({received_state})')

try:
    code = response_params['code']
except KeyError:
    raise Exception('The user declined authorization.') from None

print('Step 3. Exchange the authorization code for an access/refresh token.\n')

user_agent = (
        f'RedditWarp/{redditwarp.__version__} '
        f'{transporter.name}/{transporter.version} '
        'redditwarp.cli.refresh_token')
session = new_session(headers={'User-Agent': user_agent})
token_client = redditwarp.auth.TokenObtainmentClient(
    session,
    redditwarp.auth.const.TOKEN_OBTAINMENT_URL,
    redditwarp.auth.ClientCredentials(client_id, client_secret),
    redditwarp.auth.grants.AuthorizationCodeGrant(code, redirect_uri),
)

print('Obtaining tokens from the token server...\n')
token = token_client.fetch_token()
print(f" Access token : {token.access_token}")
print(f"Refresh token : {token.refresh_token}")
