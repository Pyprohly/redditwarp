
from typing import Optional, List

import sys
from os import path as op
from os import getenv
from configparser import ConfigParser

def get_praw_ini_potential_locations() -> List[str]:
    ini_file_name = 'praw.ini'

    package_dir = ''
    if __name__ != '__main__':
        root_package_name, _, _ = __name__.partition('.')
        modu = sys.modules[root_package_name]
        package_dir = op.dirname(modu.__file__)

    getenv2 = lambda key: getenv(key, '')
    return [
        op.join(*components, ini_file_name)
        for components in [
            (package_dir,),  # Package defaults
            (getenv2('APPDATA'),),  # Windows
            (getenv2('HOME'), '.config'),  # Linux and macOS
            (getenv2('XDG_CONFIG_HOME'),),  # Linux
            ('.',),  # Current directory
        ]
        if components[0]
    ]

def get_praw_config(config: Optional[ConfigParser] = None) -> ConfigParser:
    if config is None:
        config = ConfigParser()
    config.read(get_praw_ini_potential_locations())
    return config
