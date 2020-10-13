
from redditwarp.util.extract_id36_from_url import (
    extract_submission_id36_from_url,
    extract_comment_id36_from_url,
)

def test_extract_id36_from_submission_url() -> None:
    for url in (
        "redd.it/SUBMISSION_ID36",
        "https://redd.it/SUBMISSION_ID36",
        "https://redd.it/SUBMISSION_ID36/",
        "reddit.com/SUBMISSION_ID36",
        "www.reddit.com/SUBMISSION_ID36",
        "https://www.reddit.com/SUBMISSION_ID36",
        "https://www.reddit.com/comments/SUBMISSION_ID36",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36/_",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36/url_slug",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36/url_slug/?a=b&c=3",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36/url_slug/COMMENT_ID36?a=b&c=3",
    ):
        assert extract_submission_id36_from_url(url) == 'SUBMISSION_ID36'

def test_extract_id36_from_comment_url() -> None:
    for url in (
        "reddit.com/comments/SUBMISSION_ID36/_/COMMENT_ID36",
        "www.reddit.com/comments/SUBMISSION_ID36/_/COMMENT_ID36",
        "https://www.reddit.com/comments/SUBMISSION_ID36/_/COMMENT_ID36",
        "https://www.reddit.com/comments/SUBMISSION_ID36//COMMENT_ID36",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36/url_slug/COMMENT_ID36",
        "https://www.reddit.com/r/redditdev/comments/SUBMISSION_ID36/url_slug/COMMENT_ID36?a=b&c=3",
    ):
        assert extract_comment_id36_from_url(url) == 'COMMENT_ID36'
