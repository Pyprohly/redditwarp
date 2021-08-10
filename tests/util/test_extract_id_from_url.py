
import pytest

from redditwarp.util.extract_id_from_url import (
    extract_submission_id_from_url,
    extract_comment_id_from_url,
)

def test_extract_id_from_submission_url() -> None:
    for x in ('https', 'http'):
        url = f"{x}://www.reddit.com/comments/odg4ic"
        assert extract_submission_id_from_url(url) == 1473775572

    for x in [
        'www.reddit.com',
        'reddit.com',
        'redd.it',
        'ssl.reddit.com',
    ]:
        url = f"https://{x}/comments/odg4ic"
        assert extract_submission_id_from_url(url) == 1473775572

    for x in [
        "odg4ic",
        "comments/odg4ic",
        "comments/odg4ic/post_title",
        "r/redditdev/odg4ic/",
        "r/redditdev/comments/odg4ic/",
        "r/redditdev/comments/odg4ic/post_title",
    ]:
        url = "https://www.reddit.com/" + x
        assert extract_submission_id_from_url(url) == 1473775572

def test_extract_id_from_submission_url__bad_urls() -> None:
    def do(url: str) -> None:
        with pytest.raises(ValueError):
            extract_submission_id_from_url(url)

    # Test scheme
    do("sptth://www.reddit.com/comments/odg4ic")

    # Test netloc
    do("https://python.org/comments/odg4ic")

    # Test raise ValueError positions
    W = "https://www.reddit.com"
    do(W + "/comments/odg4ic/post_title/whats_this")
    do(W + "/r/redditdev/comments/odg4ic/post_title/whats_this")
    do(W + "/r/redditdev/odg4ic/post_title")
    do(W + "/odg4ic/post_title")

    # Test IndexErrors raise ValueError
    do(W)
    do(W + "/")
    do(W + "/comments")
    do(W + "/r")
    do(W + "/r/redditdev")
    do(W + "/r/redditdev/comments")


def test_extract_id_from_comment_url() -> None:
    for x in ('https', 'http'):
        url = f"{x}://www.reddit.com/comments/odg4ic/_/h40cl6f"
        assert extract_comment_id_from_url(url) == 37247751735

    for x in [
        'www.reddit.com',
        'reddit.com',
        'redd.it',
        'ssl.reddit.com',
    ]:
        url = f"https://{x}/comments/odg4ic/_/h40cl6f"
        assert extract_comment_id_from_url(url) == 37247751735

    for x in [
        "comments/odg4ic/_/h40cl6f",
        "r/redditdev/comments/odg4ic/_/h40cl6f",
    ]:
        url = "https://www.reddit.com/" + x
        assert extract_comment_id_from_url(url) == 37247751735

def test_extract_id_from_comment_url__bad_urls() -> None:
    def do(url: str) -> None:
        with pytest.raises(ValueError):
            extract_comment_id_from_url(url)

    # Test scheme
    do("sptth://www.reddit.com/comments/odg4ic/_/h40cl6f")

    # Test netloc
    do("https://python.org/comments/odg4ic/_/h40cl6f")

    # Test raise ValueError positions
    W = "https://www.reddit.com"
    do(W + "/r/redditdev/stnemmoc/odg4ic/_/h40cl6f")

    # Test IndexErrors raise ValueError
    do(W)
    do(W + "/")
    do(W + "/comments")
    do(W + "/comments/odg4ic")
    do(W + "/comments/odg4ic/_")
    do(W + "/r")
    do(W + "/r/redditdev")
    do(W + "/r/redditdev/comments")
    do(W + "/r/redditdev/comments/odg4ic")
    do(W + "/r/redditdev/comments/odg4ic/_")
