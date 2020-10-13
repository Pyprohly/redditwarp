
import re

_submission_id36_regex = re.compile(r'comments/(\w+)|(\w+)/?$')
_comment_id36_regex = re.compile(r'comments/\w+/\w*/(\w+)')

def extract_submission_id36_from_url(url: str) -> str:
    url, _, _ = url.partition('?')
    match = _submission_id36_regex.search(url)
    if not match:
        raise ValueError('bad url format')
    return next(x for x in match.groups() if x)

def extract_comment_id36_from_url(url: str) -> str:
    url, _, _ = url.partition('?')
    match = _comment_id36_regex.search(url)
    if not match:
        raise ValueError('bad url format')
    return match[1]
