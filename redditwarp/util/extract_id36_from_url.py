
import re

_submission_id36_regex = re.compile(r'comments/(\w+)|(\w+)/?$')
_comment_id36_regex = re.compile(r'comments/\w+/\w*/(\w+)')

def extract_id36_from_submission_url(url: str) -> str:
    url, _, _ = url.partition('?')
    match = _submission_id36_regex.search(url)
    if not match:
        raise ValueError('bad url format')
    return next(x for x in match.groups() if x)

def extract_id36_from_comment_url(url: str) -> str:
    url, _, _ = url.partition('?')
    match = _comment_id36_regex.search(url)
    if not match:
        raise ValueError('bad url format')
    return match[1]
