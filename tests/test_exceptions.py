
import pytest

from redditwarp.exceptions import raise_for_reddit_error, APIException, RedditError

null = None

def test_raise_for_reddit_error() -> None:
    json_data = {"message": "Not Found", "error": 404}
    raise_for_reddit_error(json_data)

    json_data = {"reason": "private", "message": "Forbidden", "error": 403}
    with pytest.raises(APIException) as exc_info:
        raise_for_reddit_error(json_data)
    assert not isinstance(exc_info.value, RedditError)
    assert str(exc_info.value) == "private"

    json_data = {"explanation": "Please log in to do that.", "message": "Forbidden", "reason": "USER_REQUIRED"}
    with pytest.raises(RedditError) as exc_info:
        raise_for_reddit_error(json_data)
    exc = exc_info.value
    assert exc.codename == 'USER_REQUIRED'
    assert exc.explanation == 'Please log in to do that.'
    assert exc.field == ''

    json_data = {"fields": ["subject"], "explanation": "we need something here", "message": "Bad Request", "reason": "NO_TEXT"}
    with pytest.raises(RedditError) as exc_info:
        raise_for_reddit_error(json_data)
    exc = exc_info.value
    assert exc.codename == 'NO_TEXT'
    assert exc.explanation == "we need something here"
    assert exc.field == 'subject'

    json_data = {"fields": ["to"], "explanation": null, "message": "Bad Request", "reason": "MUTED_FROM_SUBREDDIT"}
    with pytest.raises(RedditError) as exc_info:
        raise_for_reddit_error(json_data)
    exc = exc_info.value
    assert exc.codename == 'MUTED_FROM_SUBREDDIT'
    assert exc.explanation == ''
    assert exc.field == 'to'

    json_data = {"fields": [null], "explanation": null, "message": "Forbidden", "reason": "SUBREDDIT_NO_ACCESS"}
    with pytest.raises(RedditError) as exc_info:
        raise_for_reddit_error(json_data)
    exc = exc_info.value
    assert exc.codename == 'SUBREDDIT_NO_ACCESS'
    assert exc.explanation == ''
    assert exc.field == ''

    json_data = {"fields": [null], "explanation": null, "message": "Bad Request", "reason": "Must pass an id or list of ids."}
    with pytest.raises(APIException) as exc_info:
        raise_for_reddit_error(json_data)
    assert str(exc_info.value) == "Must pass an id or list of ids."

    json_data = {"json": {"errors": [["NO_LINKS", "that subreddit only allows text posts", "sr"], ["RATELIMIT", "you are doing that too much. try again in 13 minutes.", "ratelimit"]]}}
    with pytest.raises(RedditError) as exc_info:
        raise_for_reddit_error(json_data)
    exc = exc_info.value
    assert exc.codename == 'NO_LINKS'
    assert exc.explanation == "that subreddit only allows text posts"
    assert exc.field == 'sr'

    json_data = {"json": {"errors": [["LIVEUPDATE_NO_INVITE_FOUND", "there is no pending invite for that thread", null]]}}
    with pytest.raises(RedditError) as exc_info:
        raise_for_reddit_error(json_data)
    exc = exc_info.value
    assert exc.codename == 'LIVEUPDATE_NO_INVITE_FOUND'
    assert exc.explanation == "there is no pending invite for that thread"
    assert exc.field == ''
