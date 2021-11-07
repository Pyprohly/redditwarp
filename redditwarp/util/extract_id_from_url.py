
import urllib.parse
from pathlib import Path
from collections import deque

def extract_submission_id_from_url(url: str) -> int:
    urlparts = urllib.parse.urlsplit(url)
    if urlparts.scheme not in {'https', 'http'}:
        raise ValueError
    if urlparts.netloc not in {'www.reddit.com', 'reddit.com', 'redd.it', 'ssl.reddit.com'}:
        raise ValueError

    parts = deque(Path(urlparts.path).parts)

    def popq() -> str:
        try:
            return parts.popleft()
        except IndexError as cause:
            raise ValueError from cause

    t = popq()
    assert t == '/'
    val = ''
    t = popq()
    if t == 'comments':
        val = popq()
        if len(parts) > 1:
            raise ValueError
    elif t == 'r':
        popq()  # subreddit
        t = popq()
        if t == 'comments':
            val = popq()
            if len(parts) > 1:
                raise ValueError
        else:
            val = t
            if parts:
                raise ValueError
    else:
        val = t
        if parts:
            raise ValueError

    return int(val, 36)

def extract_comment_id_from_url(url: str) -> int:
    urlparts = urllib.parse.urlsplit(url)
    if urlparts.scheme not in {'https', 'http'}:
        raise ValueError
    if urlparts.netloc not in {'www.reddit.com', 'reddit.com', 'redd.it', 'ssl.reddit.com'}:
        raise ValueError

    parts = deque(Path(urlparts.path).parts)

    def popq() -> str:
        try:
            return parts.popleft()
        except IndexError as cause:
            raise ValueError from cause

    t = popq()
    assert t == '/'
    val = ''
    t = popq()
    if t == 'comments':
        popq()  # submission ID36
        popq()  # slug
        val = popq()
    elif t == 'r':
        popq()  # subreddit
        comments = popq()
        if comments != 'comments':
            raise ValueError
        popq()  # submission ID36
        popq()  # slug
        val = popq()

    return int(val, 36)
