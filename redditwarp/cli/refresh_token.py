#!/usr/bin/env python3
"""
Step through the OAuth2 Authorization Code Flow to obtain OAuth2 tokens.

Visit <https://www.reddit.com/prefs/apps> to create an app for your client.

Your app's redirect URI must *exactly* match `http://localhost:8080`.

Only one refresh token and access token can be active at a time. If either
becomes leaked, simply fetch new tokens with this tool to invalidate both.

Refresh tokens never expire.
Access tokens expire after one hour.
Authorization codes expire after 10 minutes or after use.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
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
add('--duration', choices=['temporary', 'permanent'], default='permanent', help=argparse.SUPPRESS)
add('--no-web-browser', action='store_true', help="don't launch a browser")
add('--web-browser-name', help="the web browser to open")
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
from redditwarp.http.transport.SYNC import (
    load_transport_module,
    new_session,
    get_session_underlying_library_name_and_version,
)
from redditwarp.auth.SYNC import RedditTokenObtainmentClient

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
scope: str = args.scope
redirect_uri: str = args.redirect_uri
duration: str = args.duration
no_web_browser: bool = args.no_web_browser
web_browser_name: str = args.web_browser_name
state = str(uuid.uuid4())

browser = webbrowser.get(web_browser_name)

print('\n        -~=~- Reddit OAuth2 Authorization Code Flow -~=~-\n')
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
    browser.open(url)

print('Step 2. Wait for the authorization server response and extract the authorization code.\n')

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(1)
    match = None
    while not match:
        client, addr = server.accept()
        print(addr)
        with client:
            data = client.recv(8192)
            client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

        decoded = data.strip().decode()
        print(f"```\\\n{decoded}\n```\n")
        match = re.match(r"^GET /\?([^ ]*) HTTP", decoded)

assert match is not None
query = match[1]
dl = urllib.parse.parse_qs(query)
response_params = {k: v[0] for k, v in dl.items()}

received_state = response_params['state']
if received_state != state:
    raise Exception(f'sent state ({state}) did not match received ({received_state})')

code = response_params.get('code', '')
if not code:
    raise Exception('authorization declined')

print('Step 3. Exchange the authorization code for an access/refresh token.\n')

session = new_session()
transport_name, transport_version = get_session_underlying_library_name_and_version(session)
user_agent = (
    f"RedditWarp/{redditwarp.__version__} "
    f"Python/{'.'.join(map(str, sys.version_info[:2]))} "
    f"{transport_name}/{transport_version} "
    "redditwarp.cli.refresh_token"
)
headers = {'User-Agent': user_agent}
token_client = RedditTokenObtainmentClient(
    session,
    redditwarp.auth.const.TOKEN_OBTAINMENT_URL,
    (client_id, client_secret),
    redditwarp.auth.grants.AuthorizationCodeGrant(code, redirect_uri),
    headers,
)

print('Obtaining tokens from the token server...\n')
token = token_client.fetch_token()
print(f" Access token : {token.access_token}")
print(f"Refresh token : {token.refresh_token}")
