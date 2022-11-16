#!/usr/bin/env python3
"""
Step through the OAuth2 Implicit Flow to obtain an access token.

Visit <https://www.reddit.com/prefs/apps> to create an OAuth2 application profile
for your client before running this script.

Your app's redirect URI must *exactly* match `http://localhost:8080`.

This flow requires an 'installed app' app type.
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
add('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
add('--scope', default='*', help='an OAuth2 scope string')
add('--redirect-uri', default='http://localhost:8080', help='\N{ZERO WIDTH SPACE}')
add('--duration', choices=['temporary', 'permanent'], default='permanent', help=argparse.SUPPRESS)
add('--no-web-browser', action='store_true', help="don't launch a browser")
add('--web-browser-name', help="the web browser to open")
args = parser.parse_args()
###;

import sys
import os
import uuid
import socket
import urllib.parse
import webbrowser
import signal
from functools import partial

import redditwarp
from redditwarp.http.transport.reg_SYNC import load_transport

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

load_transport()

client_id = get_client_cred_input(
        (args.client_id_opt or args.client_id),
        'Client ID: ', 'redditwarp_client_id')
scope: str = args.scope
redirect_uri: str = args.redirect_uri
duration: str = args.duration
no_web_browser: bool = args.no_web_browser
web_browser_name: str = args.web_browser_name
state = str(uuid.uuid4())

port = urllib.parse.urlsplit(redirect_uri).port
if port is None:
    raise Exception('could not determine the port number from the redirect uri')

browser = webbrowser.get(web_browser_name)

print('\n        -~=~- Reddit OAuth2 Implicit Flow -~=~-\n')
print('Step 1. Build the authorization URL and direct the user to the authorization server.\n')

params = {
    'response_type': 'token',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scope,
    'state': state,
}
url = "%s?%s" % (redditwarp.auth.const.AUTHORIZATION_URL, urllib.parse.urlencode(params))

print(url)
print()

if not no_web_browser:
    browser.open(url)

print('Step 2. Wait for the authorization server response and extract the authorization code.\n')

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', port))
    server.listen(1)

    client, addr = server.accept()
    with client:
        data = client.recv(8192)
        client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

prompt = 'Enter the address bar URL: \\\n'
while not (redirected_url := input(prompt)):
    pass

urlparts = urllib.parse.urlsplit(redirected_url)
dl = urllib.parse.parse_qs(urlparts.fragment)
response_params = {k: v[0] for k, v in dl.items()}

if state and 'state' not in response_params:
    raise Exception('no state value received')

received_state = response_params['state']
if received_state != state:
    raise Exception(f'sent state ({state}) did not match received ({received_state})')

print()
access_token = response_params['access_token']
print(f'Access token: {access_token}')
