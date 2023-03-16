#!/usr/bin/env python
from __future__ import annotations
from typing import IO, Optional

import sys
import subprocess
from pathlib import Path
import shutil
import shlex


def print_usage(file: Optional[IO[str]] = None) -> None:
    if file is None:
        file = sys.stdout
    print('''\
Usage:
    prog full
    prog clean-all
''', end='', file=file)

def do_build_main() -> None:
    subprocess.run(['make', 'html'])

def do_build_apidoc() -> None:
    pkg = './redditwarp'
    if not Path(pkg).is_dir():
        pkg = '../redditwarp'

    subprocess.run(shlex.split('''\
sphinx-apidoc -ef
        -H "API Reference"
        --tocfile=index
        -t source/_templates/apidoc
        -o generated/api
''') + [pkg])

def do_clean_build() -> None:
    subprocess.run(['make', 'clean'])

def do_clean_generated() -> None:
    path = Path('generated')
    if not path.is_dir():
        return
    print("Removing everything under 'generated'...")
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


if (
    len(sys.argv) == 1
    or sys.argv[1] == '--help'
):
    print_usage()
    sys.exit(0)

itr = iter(sys.argv)
next(itr)
for arg in itr:
    if arg == 'main':
        do_build_main()
    elif arg == 'apidoc':
        do_build_apidoc()
    elif arg == 'full':
        do_build_apidoc()
        do_build_main()

    elif arg in 'clean-build':
        do_clean_build()
    elif arg == 'clean-generated':
        do_clean_generated()
    elif arg == 'clean-all':
        do_clean_build()
        do_clean_generated()

    else:
        if arg.startswith('-'):
            print('Bad recipe name: ' + arg, file=sys.stderr)
            sys.exit(1)

        subprocess.run(['make', arg])
