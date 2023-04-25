
=========
Streaming
=========

Streams are used to monitor listings for new items. This is beneficial for bots
that need to discover and respond to new events in near real time.

.. literalinclude:: _assets/streaming_demo.py

Because Reddit listings don't support websockets or webhooks, the client must
simulate streaming by polling continuously for new items. RedditWarp's streams
are simple to use, having little to no configuration options, and are designed
to be automatically efficient and accurate. It will reduce polling frequency
when it can't connect to the server and speed up polling when the listing is
more active.

The steaming logic is based on paginators.

.. csv-table:: Streamable listings
   :header: "Pagination source", "Stream creator function"

   "`client.p.message.pulls.inbox()`","`message_ASYNC.create_inbox_message_stream()`"
   "`client.p.message.pulls.mentions()`","`message_ASYNC.create_mentions_message_stream()`"
   "`client.p.moderation.pull_actions()`","`moderation_ASYNC.create_action_log_stream()`"
   "`client.p.modmail.pull.new()`","`modmail_ASYNC.create_conversation_message_new_stream()`"
   "`client.p.modmail.pull.join_requests()`","`modmail_ASYNC.create_conversation_message_join_request_stream()`"
   "`client.p.subreddit.pull.new()`","`subreddit_ASYNC.create_submission_stream()`"
   "`client.p.subreddit.pull_new_comments()`","`subreddit_ASYNC.create_comment_stream()`"
   "`client.p.subreddit.pulls.new()`","`subreddit_ASYNC.create_subreddit_stream()`"
   "`client.p.user.pull_user_subreddits.new()`","`user_ASYNC.create_user_subreddit_stream()`"

Stream objects have two events on them: `output` and `error`. You can attach
event handlers to these dispatchers by passing a single-argument function to
their `attach()` method.

It is important to add thorough error handling logic to event handler code as
any exceptions thrown from the attached handlers will be propagated and crash
the program as per usual. Note that the `error` event is for errors generated
by the streaming mechanism and not for errors caused by user code.

The `.attach()` method returns `None`, so be careful when stacking them as
decorators. If you prefer the look of decorators, you can use the `passthru`
utility to force functions to return their input.

::

   from redditwarp.util.passthru import passthru

   ...

   @passthru(comment_stream.error.attach)
   @passthru(submission_stream.error.attach)
   async def _(exc: Exception) -> None:
       print('<>', file=sys.stderr)
       traceback.print_exception(exc.__class__, exc, exc.__traceback__)
       print('</>', file=sys.stderr)

The `flow()` method is used to run the steams. Because async streams are
awaitable they can also be passed directly to `asyncio.gather()` instead.

Although streams are useful for discovering new resources quickly, they do not
guarantee that an uncovered item will actually be 'new'. It is recommended to
check the creation date of a resource if being new is important to your
handler's logic.

The streams provide the invariant that an item from the stream will never be
repeated.
