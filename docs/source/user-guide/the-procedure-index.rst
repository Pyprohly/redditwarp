
===================
The Procedure Index
===================

All the possible API calls can be found under `client.p`. Because there are so
many methods, they have been grouped under sub-objects, organised by resource
kind.

::

   >>> import redditwarp.SYNC
   >>> client = redditwarp.SYNC.Client()
   >>> client.p.
   client.p.account              client.p.misc
   client.p.collection           client.p.moderation
   client.p.comment              client.p.modmail
   client.p.comment_tree         client.p.ping()
   client.p.custom_feed          client.p.submission
   client.p.draft                client.p.subreddit
   client.p.flair                client.p.subreddit_style_new
   client.p.flair_emoji          client.p.subreddit_style_old
   client.p.front                client.p.user
   client.p.live_thread          client.p.widget
   client.p.message              client.p.wiki
   >>> client.p.

Discovering procedures
----------------------

The organisation of the methods by resource kind makes it easy to locate API
procedures.

For example, let's say we want to post a submission to a subreddit. Since this
is a submission operation, the procedure will be found somewhere under
`client.p.submission`.

While actively coding, IDEs will greatly help in navigating the procedure
index. If you're not using an IDE, we could write `client.p.submission.<TAB>`
in an interactive Python REPL terminal session to view all the
submission-related procedures.

::

   >>> client.p.submission.
   client.p.submission.MediaUploading(               client.p.submission.media_uploading(
   client.p.submission.apply_removal_reason(         client.p.submission.pin_to_profile(
   client.p.submission.approve(                      client.p.submission.remove(
   client.p.submission.bulk_fetch(                   client.p.submission.remove_spam(
   client.p.submission.bulk_hide(                    client.p.submission.reply(
   client.p.submission.bulk_unhide(                  client.p.submission.save(
   client.p.submission.create_crosspost(             client.p.submission.search(
   client.p.submission.create_gallery_post(          client.p.submission.send_removal_comment(
   client.p.submission.create_image_post(            client.p.submission.send_removal_message(
   client.p.submission.create_link_post(             client.p.submission.set_contest_mode(
   client.p.submission.create_poll_post(             client.p.submission.set_event_time(
   client.p.submission.create_text_post(             client.p.submission.set_suggested_sort(
   client.p.submission.create_video_post(            client.p.submission.snooze_reports(
   client.p.submission.delete(                       client.p.submission.sticky(
   client.p.submission.disable_reply_notifications(  client.p.submission.undistinguish(
   client.p.submission.distinguish(                  client.p.submission.unfollow_event(
   client.p.submission.duplicates(                   client.p.submission.unhide(
   client.p.submission.edit_text_post_body(          client.p.submission.unignore_reports(
   client.p.submission.enable_reply_notifications(   client.p.submission.unlock(
   client.p.submission.fetch(                        client.p.submission.unmark_nsfw(
   client.p.submission.follow_event(                 client.p.submission.unmark_spoiler(
   client.p.submission.get(                          client.p.submission.unpin_from_profile(
   client.p.submission.hide(                         client.p.submission.unsave(
   client.p.submission.ignore_reports(               client.p.submission.unsnooze_reports(
   client.p.submission.lock(                         client.p.submission.unsticky(
   client.p.submission.mark_nsfw(                    client.p.submission.vote(
   client.p.submission.mark_spoiler(
   >>> client.p.submission.

Most resource kind sub-object groups will have methods `get()` and `fetch()`.
These methods are usually used to retrieve information about a specific
resource by its ID.

::

   subm = client.p.submission.fetch('cqufij')
   print(subm.author_display_name)
   print(subm.title)
   print(subm.created_at)
   print(subm.permalink)

Get vs. fetch
-------------

The `get()` and `fetch()` methods are used to retrieve a resource by ID.
These procedures are shared by the majority of resource kinds in the procedure
index. The difference between them is that `fetch()` raises an exception when
it fails to retrieve a resource, whereas `get()` will return `None`.

The exception type thrown by `fetch()` is not sugar-coated and may vary based
on the behaviour of the underlying endpoint. In some cases, the API does not
produce an error when a retrieval fails and instead returns no information.
RedditWarp will force an exception to occur in these instances by raising a
synthetic :exc:`redditwarp.exceptions.NoResultException` exception.

::

   >>> client.p.user.fetch_by_name('sdfaxzzdfv')
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "/Users/danpro/Desktop/redditwarp/redditwarp/siteprocs/user/SYNC.py", line 108, in fetch_by_name
       root = self._client.request('GET', f'/user/{name}/about')
     File "/Users/danpro/Desktop/redditwarp/redditwarp/client_SYNC.py", line 226, in request
       resp.ensure_successful_status()
     File "/Users/danpro/Desktop/redditwarp/redditwarp/http/response.py", line 31, in ensure_successful_status
       ensure_successful_status(self.status)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/http/exceptions.py", line 124, in ensure_successful_status
       raise_now(n)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/http/exceptions.py", line 119, in raise_now
       raise get_status_code_exception_class_by_status_code(n)(status_code=n)
   redditwarp.http.exceptions.StatusCodeExceptionTypes.NotFound: 404 Not Found
   >>> client.p.submission.fetch(999)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "/Users/danpro/Desktop/redditwarp/redditwarp/siteprocs/submission/fetch_SYNC.py", line 22, in __call__
       return self.by_id36(id36)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/siteprocs/submission/fetch_SYNC.py", line 32, in by_id36
       raise NoResultException('target not found')
   redditwarp.exceptions.NoResultException: target not found

When using the `get()` method, it's important to explicitly check if the
returned object is `None` to maintain the type-safety of your program.
Your IDE or type-checker should notify you if you forget to do this.

In general, prefer the `fetch()` method when you expect the resource to exist,
and `get()` when you don't care as much about whether the resource exists.

Exceptions
----------

View the docstring of a procedure index method to learn about the possible
exceptions it could raise. Note that the exceptions listed may not
be exhaustive; for example, if Reddit servers are down, many API requests
could result in a 500 HTTP status code exception.

The :exc:`redditwarp.http.exceptions.StatusCodeException` exception is a
common exception type that occurs from API procedures.
Instances of this exception have a `status_code` attribute.

::

   try:
       user = client.p.user.fetch_by_name('sdfaxzzdfv')
   except redditwarp.http.exceptions.StatusCodeException as e:
       if e.status_code == 404:
           print('User not found')
       else:
           print('Unknown error occurred')
           raise
   else:
       print(user.total_karma)

The status code exception gets raised as a last resort when more detailed error
information cannot be found in the response data. Most API errors are
reported in the form of a :exc:`redditwarp.exceptions.RedditError` exception.

There are three string fields on `RedditError`: `label`, `explanation`, and `field`.
The `label` field will always be filled out, while the other two could be empty
strings, although the `explanation` field is usually not empty, unlike `field`.

When catching the `RedditError` exception, it is useful to check against `label`.

::

   try:
       client.p.message.send(
               'TheSantaManta', "Evil Christmas wish",
               "Dear SantaManta, I want the world for Christmas.")
   except redditwarp.exceptions.RedditError as e:
       if e.label == 'USER_DOESNT_EXIST':
           print('The user does not exist')
       else:
           raise

If we didn't catch the exception, this is what the exception traceback would
look like.

::

   Traceback (most recent call last):
     File "<stdin>", line 2, in <module>
     File "/Users/danpro/Desktop/redditwarp/redditwarp/siteprocs/message/SYNC.py", line 31, in send
       self._client.request('POST', '/api/compose', data=req_data)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/client_SYNC.py", line 236, in request
       snub(json_data)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/exceptions.py", line 177, in raise_for_reddit_error
       raise RedditError(label=label, explanation=explanation, field=field)
   redditwarp.exceptions.RedditError: USER_DOESNT_EXIST: "that user doesn't exist" -> to

Bulk retrieval
--------------

Bulk operations are composed of batched API requests. Bulk operation procedures
typically return an iterator object. This iterator object should be consumed to
evaluate all the batched network requests.

If the iterator doesn't return anything useful, an empty `for` loop will do the
trick. E.g.::

   it: Iterable[int] = [...]
   itr = client.p.modmail.conversation.bulk_mark_read(it)
   for _ in itr:
       pass

Network errors are possible during iteration, and an exception can be thrown on
the `for` loop line. The iterator, however, won't break if this happens and it
can be reentered if needed.

::

   itr = client.p.submission.bulk_fetch([...])
   while True:
       try:
           for item in itr:
               process_item(item)
       except Exception:
           time.sleep(60)
           continue
       break

The downside of this approach is that the `try` block may be covering too much,
since it's not possible in Python syntax to put a `try..except` around only the
`for` loop line and not its body. For more precise control over error handling,
it is preferable to evaluate call chunks directly.

Use `get_chunking_iterator()` to access the underlying call chunks::

   itr = client.p.submission.bulk_fetch([...])
   chunks = itr.get_chunking_iterator()
   for chunk in chunks:
       while True:
           try:
               results = chunk()
           except Exception:
               time.sleep(60)
               continue
           break
       for item in results:
           process_item(item)

There are actually two types of iterators that are returned by `bulk_*` methods: a
:class:`~redditwarp.iterators.call_chunk_calling_iterator.CallChunkCallingIterator`
and a
:class:`~redditwarp.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`.
The former
returns single objects (often `None`), while the latter returns a sequence of
objects when its call chunks are evaluated.

Both `CallChunkCallingIterator` and `CallChunkChainingIterator` objects have a
`.current_callable` property that will be assigned a callable object if a
call chunk call fails during iteration, otherwise it is `None`.

The `CallChunkChainingIterator` object also has a `.current_iterator` property
which contains an iterator that may be populated if the main iterator was
interrupted.

::

   itr: CallChunkChainingIterator[Submission] = client.p.submission.bulk_fetch([...])
   try:
       for item in itr:
           process_item(item)
   except Exception:
       pass

   # The `itr.current_iterator` object will be a non-empty iterator
   # if an exception was caused by the `process_item(item)` line above.
   for item in itr.current_iterator:
       process_item(item)

   # The `itr.current_callable` attribute will be non-`None`
   # if an exception was caused by the `for item in itr:` line above.
   if itr.current_callable is not None:
       for item in itr.current_callable():
           process_item(item)
       itr.current_callable = None

Last thing to note, the iterator modules don't have names with `SYNC`/`ASYNC`.
The reason for this is because an async iterator can be made to accept sync or
async iterable input, so there could theoretically be two versions of an async
iterator. Additionally, it can occasionally make sense to use a sync iterator
in an async program.

::

   # SYNC
   from redditwarp.iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
   # ASYNC
   from redditwarp.iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
