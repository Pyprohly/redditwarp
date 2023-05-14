
# RedditWarp

[![Latest version](https://img.shields.io/pypi/v/redditwarp)](https://pypi.org/p/redditwarp/)
![Supported Python versions](https://img.shields.io/pypi/pyversions/redditwarp)
[![Discord guild](https://img.shields.io/discord/1084793643673600062?logo=discord&logoColor=white&logoWidth=20&label=&labelColor=5865F2&color=7289DA)](http://pyprohly.github.io/redditwarp/discord-invite)

A comprehensive, type-complete, easy-to-learn Python Reddit API wrapper.

RedditWarp is a Python library that simplifies working with the Reddit API.
It handles the complexities of the Reddit API in a way that is comprehensive,
highly discoverable, and static-type conscious. It includes a variety of useful
tools to facilitate a wide range of use cases, and even provides tools for
accessing the API in ways previously not possible.

Look how easy it is to use:

```python
import redditwarp.SYNC

client = redditwarp.SYNC.Client()

it = client.p.front.pull.hot(5)
l = list(it)
for subm in l:
    print("r/{0.subreddit.name} | {0.id36}+ ^{0.score} | {0.title!r:.80}".format(subm))
```

## Features

* A consistent and easy-to-use programming interface.
* Modern type-complete codebase.
* Sync and asynchronous IO support.
* Automatic rate limit handling.
* A comprehensive and discoverable index of API procedures.
* Model classes that are fully typed and sensibly wrap API structures.
* Formal data structures to facilitate comment tree traversals and pagination.
* HTTP transport library agnosticism.
* OAuth2 tooling and CLI utilities to help manage auth tokens.
* A simple event-based listing endpoint streaming framework.

## Installation

**Requires Python 3.8+.**
Type annotations may use 3.9 features.
Code examples will assume 3.10.

Install/update:

    pip install -U redditwarp

## Demonstration

<details open>
  <summary>Examples</summary>

```python
import redditwarp.SYNC

client = redditwarp.SYNC.Client()

# Display the first 5 submissions on the Reddit frontpage.
it = client.p.front.pull.hot(5)
l = list(it)
for subm in l:
    print("r/{0.subreddit.name} | {0.id36}+ ^{0.score} | {0.title!r:.80}".format(subm))

# How many subscribers does r/Python have?
subr = client.p.subreddit.fetch_by_name('Python')
print(subr.subscriber_count)

# Display the top submission of the week in the r/YouShouldKnow subreddit.
m = next(client.p.subreddit.pull.top('YouShouldKnow', amount=1, time='week'))
print(f'''\
{m.permalink}
{m.id36}+ ^{m.score} | {m.title}
Submitted {m.created_at.astimezone().ctime()}{' *' if m.is_edited else ''} \
by u/{m.author_display_name} to r/{m.subreddit.name}
''')

# Get the first comment of a submission.
tree_node = client.p.comment_tree.fetch(int('uc8i1g', 36), sort='top', limit=1)
c = tree_node.children[0].value
print(f'''\
{c.submission.id36}+{c.id36} ^{c.score}
u/{c.author_display_name} says:
{c.body}
''')

# List the moderators of r/redditdev.
it1 = client.p.moderation.pull_users.moderators('redditdev')
for mod in it1:
    print(mod.name)
```

</details>

<details>
  <summary>More examples</summary>

```python
# ...

# Need credentials for these next few API calls.
CLIENT_ID = '...'
CLIENT_SECRET = '...'
REFRESH_TOKEN = '...'
client1 = redditwarp.SYNC.Client(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

# Who am I?
me = client1.p.account.fetch()
print(f"Hello u/{me.name}!")

# Show my last 5 comments.
it2 = client.p.user.pull.comments(me.name, 5)
for comm in it2:
    print('###')
    print(comm.body)

# Show my last 10 saved items.
from redditwarp.models.submission_SYNC import Submission
from redditwarp.models.comment_SYNC import Comment
it3 = client1.p.user.pull.saved(me.name, 10)
l = list(it3)
for obj in l:
    print('###')
    match obj:
        case Submission() as m:
            print(f'''\
{m.permalink}
{m.id36}+ ^{m.score} | {m.title}
Submitted {m.created_at.astimezone().ctime()}{' *' if m.is_edited else ''} \
by u/{m.author_display_name} to r/{m.subreddit.name}
''')
        case Comment() as c:
            print(f'''\
{c.permalink}
{c.submission.id36}+{c.id36} ^{c.score}
u/{c.author_display_name} says:
{c.body}
''')

# Submit a link post to r/test.
subm_id = client1.p.submission.create_link_post('test',
        "Check out this cool website", "https://www.reddit.com")

# Reply to a submission.
from redditwarp.util.extract_id_from_url import extract_submission_id_from_url
idn = extract_submission_id_from_url("https://www.reddit.com/comments/5e1az9")
comm1 = client1.p.submission.reply(idn, "Pretty cool stuff!")

# Delete the post and the comment reply.
client1.p.submission.delete(subm_id)
client1.p.comment.delete(comm1.id)
```

</details>

<details>
  <summary>Streaming example</summary>

```python
#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redditwarp.models.submission_ASYNC import Submission

import asyncio

import redditwarp.ASYNC
from redditwarp.streaming.makers.subreddit_ASYNC import create_submission_stream
from redditwarp.streaming.ASYNC import flow

async def main() -> None:
    client = redditwarp.ASYNC.Client()
    async with client:
        submission_stream = create_submission_stream(client, 'AskReddit')

        @submission_stream.output.attach
        async def _(subm: Submission) -> None:
            print(subm.id36, '~', subm.title)

        @submission_stream.error.attach
        async def _(exc: Exception) -> None:
            print('ERROR:', repr(exc))

        await flow(submission_stream)

asyncio.run(main())
```

</details>

## Support

Post any questions you have to [r/redditdev].

[r/redditdev]: https://www.reddit.com/r/redditdev/

Join the conversation in the RedditWarp [Discord guild].

[Discord guild]: http://pyprohly.github.io/redditwarp/discord-invite

## Links

* [Repository](https://github.com/Pyprohly/redditwarp)
* [PyPI](https://pypi.org/p/redditwarp/)
* [Documentation](https://redditwarp.readthedocs.io/)
* [r/redditdev]
* [Discord guild]
