#!/usr/bin/env python
"""
Run `.refresh_token` with the `--access-token-only` flag.
"""
import runpy
runpy.run_module('redditwarp.cli.refresh_token', init_globals={
        '?access_token_only': True, '?description': __doc__})
