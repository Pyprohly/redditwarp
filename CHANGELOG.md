[//]: # (https://keepachangelog.com/en/1.1.0/)

# Changelog

## 1.3.0 - 2024-07-01

### Changed

- Renamed module `reddit.http.misc` to `misc_handlers`.
- The HTTP transport module registration system has been reworked:

  - The way you select an HTTP transport module has changed.
    You now use a function: `set_transport_adapter_module()`.
  - The `load_transport()` function has been replaced by `get_transport_adapter_module()`.
  - Moved `redditwarp.http.transport.reg_(A)SYNC.new_connector()` to
    `redditwarp.http.transport.auto_(A)SYNC`.
  - Moved `redditwarp.http.transport.connector_(A)SYNC` to `redditwarp.http`.

### Removed

- The pushshift module.
- The `connector` parameter from the `build_reddit_http_client()` functions.

### Fixed

- Python Urllib transport not working. (Thanks 'rodz' @old_guilhermerodz from Discord.)
- Submission model creation breaking when the backing field for the `gallery_link` attribute was
  missing in some rare cases. (Thanks @cossack_ua from Discord.)
- Dark client rate limiter wasn't actually being used.

## 1.2.0 - 2023-08-29

### Added

- `ApplyFormData` and friends in new module `redditwarp.http.misc.apply_form_data_(A)SYNC`.
- Parameter `body` to all post creation methods.
- `client.http.last.response_queue`.
- Fields `participant` and `participant_subreddit` to modmail `ConversationInfo` model.
- `connector` parameter to `build_reddit_http_client` functions.

### Changed

- The rate limiting algorithm has been improved to be simpler and cleaner, and is now consistent
  between both sync and async worlds.
- Updated modmail section due to API changes.
- The `mod_actions` attribute on `ConversationAggregate` has been renamed to `actions`.
- The model loader function `load_conversation_aggregate` now takes a single data dictionary.

### Removed

- Legacy submission creation procedures `client.p.submission.create_*_post()`.
  Use the `client.p.submission.create.*()` methods instead.
- Return value from submission creation procedures.
- The `resubmit` parameter from the link post creation procedure.
- `client.p.modmail.conversation.create()`.
  Use `.create_to_user()` or `.create_to_subreddit()` instead.
- Modmail classes `*UserDossierConversationAggregate`.

### Fixed

- `TokenBucket` exceeding capacity when a negative consume value was used.
- Cross post creation procedure `client.p.submission.create.cross()`.
- Modmail procedures that broke due to changes in API.

## 1.1.0 - 2023-05-15

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

### Fixed

- There was a bug in the docs for the BFS-2 tree traversal algorithm recipe causing output to be
  reversed. The lines that use `pop()` should instead be `popleft()`.
- Fix modmail streaming logic.
- Add zero-arg constructor and `__reversed__` to `redditwarp.util.OrderedSet`.

## 1.0.1 - 2023-04-27

### Changed

- Update .readthedocs.yaml so that ReadTheDocs can build the docs for a tagged release directly.
