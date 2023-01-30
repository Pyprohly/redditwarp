
from __future__ import annotations
from typing import Optional, Sequence

from .praw_config import get_praw_config
from ..client_ASYNC import Client

def client_from_praw_config(section_name: str, *, filepath: Optional[str] = None) -> Client:
    config = get_praw_config(filepath)
    section_name = section_name or config.default_section
    try:
        section = config[section_name]
    except KeyError:
        empty = not any(s.values() for s in config.values())
        msg = f"No section named {section_name!r} in{' empty' if empty else ''} praw.ini config."
        class StrReprStr(str):
            def __repr__(self) -> str:
                return str(self)
        raise KeyError(StrReprStr(msg)) from None

    get = section.get
    grant_creds: Sequence[str] = ()
    if refresh_token := get('refresh_token'):
        grant_creds = (refresh_token,)
    elif (username := get('username')) and (password := get('password')):
        grant_creds = (username, password)
    client = Client(
        section['client_id'],
        section['client_secret'],
        *grant_creds,
    )
    if x := get('user_agent'):
        client.set_user_agent(x)
    return client
