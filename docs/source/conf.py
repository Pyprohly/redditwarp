"""Configuration file for the Sphinx documentation builder."""

from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import sphinx.util.tags
    tags: sphinx.util.tags.Tags = ...  # type: ignore

import sys

def fn() -> None:
    from typing import TYPE_CHECKING, Union
    if TYPE_CHECKING:
        from types import ModuleType
        from importlib.machinery import ModuleSpec
        from os import PathLike

    import importlib.util

    def load_spec_from_file_location(name: str,
            location: Union[str, bytes, PathLike[str], PathLike[bytes]]) -> ModuleSpec:
        spec = importlib.util.spec_from_file_location(name, location)
        if spec is None:
            raise RuntimeError(f'module spec not found: {name} ({str(location)})')
        return spec

    def import_module_from_spec(spec: ModuleSpec) -> ModuleType:
        if spec.loader is None:
            raise RuntimeError('spec has no loader')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    for location in [
        '../redditwarp/__init__.py',
        '../../redditwarp/__init__.py',
    ]:
        spec = load_spec_from_file_location('redditwarp', location)
        try:
            import_module_from_spec(spec)
        except FileNotFoundError:
            continue
        break

fn()

if 'redditwarp' not in sys.modules:
    raise Exception('redditwarp module not located in expected position')

import redditwarp


import os.path as op


project = 'RedditWarp'
copyright = '2023, Pyprohly'
author = 'Pyprohly'
release = redditwarp.__version__



default_role = 'code'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_inline_tabs',
]
exclude_patterns: list[str] = []
suppress_warnings: list[str] = []

if op.isfile('api/index.rst'):
    tags.add('apidoc')
else:
    exclude_patterns.append('api/index.rst')
    suppress_warnings.extend([
        'ref.doc',
        # 'toc.excluded',
    ])



autodoc_member_order = 'bysource'
toc_object_entries_show_parents = 'hide'

'''
With `autodoc_typehints = 'signature'` (the default), type annotations are shown in signatures.
With `autodoc_typehints = 'none'`, type annotations are not shown.

If I let `autodoc_typehints = 'signature'` then I get hundreds of these warnings:

    "more than one target found for cross-reference %r: %s"

E.g.,1:

    /Users/danpro/Desktop/redditwarp-docs/redditwarp/streaming/makers/user_SYNC.py:
    docstring of redditwarp.streaming.makers.user_SYNC.make_user_subreddit_stream:1:
    WARNING: more than one target found for cross-reference 'Subreddit':
    redditwarp.models.comment.Comment.Subreddit,
    redditwarp.models.comment.LooseComment.Subreddit,
    redditwarp.models.my_account.MyAccount.Subreddit,
    redditwarp.models.submission.Submission.Subreddit,
    redditwarp.models.subreddit.Subreddit,
    redditwarp.models.subreddit_ASYNC.Subreddit,
    redditwarp.models.subreddit_SYNC.Subreddit,
    redditwarp.models.user.User.Subreddit,
    redditwarp.models.wiki.WikiPageRevisionAuthorUser.Subreddit

E.g.,2:

    /Users/danpro/Desktop/redditwarp-docs/redditwarp/streaming/makers/user_SYNC.py:
    docstring of redditwarp.streaming.makers.user_SYNC.create_user_subreddit_stream:1:
    WARNING: more than one target found for cross-reference 'Client':
    redditwarp.client_ASYNC.Client,
    redditwarp.client_SYNC.Client

Sphinx has no setting to disable the automatic function signature
cross-reference linking, and I can't just ignore these warnings
because it cross-references incorrectly.
'''
if not True:
    autodoc_typehints = 'none'
else:
    def fn1() -> None:
        from typing import Any

        import inspect

        from sphinx.domains.python import PythonDomain

        old_find_obj = PythonDomain.find_obj

        def find_obj(*args: Any, **kwargs: Any) -> Any:
            matches = old_find_obj(*args, **kwargs)
            if len(matches) <= 1:
                return matches

            frame = inspect.currentframe()
            if frame is None: raise RuntimeError
            prev_frame = frame.f_back
            if prev_frame is None: raise RuntimeError

            if prev_frame.f_code.co_name == 'resolve_xref':
                return []
            return matches

        PythonDomain.find_obj = find_obj  # type: ignore

    fn1()



html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']
