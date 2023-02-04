
from __future__ import annotations
from typing import Sequence, Optional

import sys
import os.path as op
from os import getenv
from configparser import ConfigParser

def _safe_getenv(key: str) -> str:
    return getenv(key, '')

def get_praw_ini_potential_locations() -> Sequence[str]:
    """Return a list of potential `praw.ini` locations."""
    root_pkg_dirname = ''
    if __name__ != '__main__':
        root_pkg_name, _, _ = __name__.partition('.')
        root_pkg_module = sys.modules[root_pkg_name]
        root_pkg_dirname = op.dirname(root_pkg_module.__file__ or '')

    return [
        op.join(*path_components, 'praw.ini')
        for path_components in [
            [root_pkg_dirname],  # Package defaults
            [_safe_getenv('APPDATA')],  # Windows
            [_safe_getenv('HOME'), '.config'],  # Linux and macOS
            [_safe_getenv('XDG_CONFIG_HOME')],  # Linux
            ['.'],  # Current directory
        ]
        if path_components[0]
    ]

def get_praw_config(filepath: Optional[str] = None) -> ConfigParser:
    """Return a `ConfigParser` initialised with the standard `praw.ini` locations."""
    config = ConfigParser()
    config.read(get_praw_ini_potential_locations() if filepath is None else filepath)
    return config
