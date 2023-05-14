[//]: # (https://keepachangelog.com/en/1.1.0/)

# Changelog

## 1.1.0

### Added

- Add configure post flair post appearance API procedure.
  (I.e., `client.p.flair.post_appearance.config()`.)
- Allow API procedures to accept string IDs.
- Add `idn` attribute as alias to `id` on model classes that have `id36`.
- Add middleware injection feature. (I.e., `client.http.having_additional_middleware()`.)
- Various class aliases have been added:

  - Alias `CrossPost` to `CrosspostSubmission` in `redditwarp.models.submission_(A)SYNC`.
  - Alias `DepthMoreComments` to `ContinueThisThread` in `redditwarp.models.more_comments_(A)SYNC`.
  - Alias `BreadthMoreComments` to `LoadMoreComments` in `redditwarp.models.more_comments_(A)SYNC`.
  - Alias `DarkClient` to `Client` in `redditwarp.dark.client_(A)SYNC`.
  - Allow import of `load_transport` and `new_connector` from `redditwarp.http.(A)SYNC`.

- Alias `client.p.submission.create_cross_post()` to `create_crosspost()`.
  This is for consistency with the other `create_*_post()` methods.
- Add `client.p.submission.create` method group. This is the new way to create submissions.
  All the `client.p.submission.create_*_post()` methods are aliases to the
  `client.p.submission.create.*()` methods.
- Add general upload lease class. I.e., `redditwarp.models.upload_lease.UploadLease`.
  Many of the specialised upload lease classes are no longer needed and are aliased to the general
  upload lease class now.

### Fixed

- There was a bug in the docs for the BFS-2 tree traversal algorithm recipe causing output to be
  reversed. The lines that use `pop()` should instead be `popleft()`.
- Fix modmail streaming logic.
- Add zero-arg constructor and `__reversed__` to `redditwarp.util.OrderedSet`.

### Changed

- Many API procedures with single arguments `idn` have been renamed to `idy` to reflect the fact
  that both strings and integers are supported.
- Rename modmail stream maker functions. All the modmail folders are now streamable.
- The streaming logic no longer checks on start up if a given paginator has been used. Users should
  either call `reset()` on a paginator before passing it to a stream if that was the intention, or
  use the `past` parameter.
- Various tweaks to documentation wording.

### Removed

- The `seen` parameter has been removed from stream maker functions. Use `past` instead.
- ID extractor functions from stream maker modules. ID extraction is a stream-specific
  implementation detail.
- Module `redditwarp.streaming.stream_(A)SYNC`.

## 1.0.1 - 2023-04-27

### Changed

- Update .readthedocs.yaml so that ReadTheDocs can build the docs for a tagged release directly.
