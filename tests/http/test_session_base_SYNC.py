
from __future__ import annotations
from typing import Optional

# import contextvars

from redditwarp.http.session_base_SYNC import SessionBase
from redditwarp.http.response import Response
from redditwarp.http.request import Request

class MySession(SessionBase):
    def __init__(self) -> None:
        super().__init__()
        self.timeout = 100
        # self.timeout_used: float = 0

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        # self.timeout_used = self._get_effective_timeout_value(timeout)
        return Response(200, {}, b'')

requ = Request('', '', params={}, headers={}, payload=None)

# Unused idea for now
'''
class TestTimeoutAsMethod:
    def test_basics(self) -> None:
        sess = MySession()
        with sess.timeout_as(3):
            sess.send(requ)
            assert sess.timeout_used == 3
            sess.send(requ)
            assert sess.timeout_used == 3
        sess.send(requ)
        assert sess.timeout_used == 100

        sess.timeout_as(9)
        sess.send(requ)
        assert sess.timeout_used == 100

    def test_timeout_precedence(self) -> None:
        sess = MySession()
        assert sess.timeout_used == 0

        sess.send(requ)
        assert sess.timeout_used == 100

        sess.send(requ, timeout=200)
        assert sess.timeout_used == 200

        with sess.timeout_as(300):
            sess.send(requ, timeout=200)
        assert sess.timeout_used == 300

    def test_nested(self) -> None:
        sess = MySession()
        with sess.timeout_as(1):
            sess.send(requ)
            assert sess.timeout_used == 1

            with sess.timeout_as(2):
                sess.send(requ)
                assert sess.timeout_used == 2

            sess.send(requ)
            assert sess.timeout_used == 1

        sess.send(requ)
        assert sess.timeout_used == 100

    def test_reuse(self) -> None:
        sess = MySession()
        timeout_context = sess.timeout_as(5)
        with timeout_context:
            sess.send(requ)
            assert sess.timeout_used == 5

        sess.send(requ)
        assert sess.timeout_used == 100

        with timeout_context:
            sess.send(requ)
            assert sess.timeout_used == 5

    def test_reentrancy(self) -> None:
        sess = MySession()
        timeout_context = sess.timeout_as(6)
        with timeout_context:
            sess.send(requ)
            assert sess.timeout_used == 6

            with timeout_context:
                sess.send(requ)
                assert sess.timeout_used == 6

            sess.send(requ)
            assert sess.timeout_used == 6

        sess.send(requ)
        assert sess.timeout_used == 100

    def test_other_instances_arent_affected(self) -> None:
        sess1 = MySession()
        sess2 = MySession()

        with sess1.timeout_as(4):
            sess1.send(requ)
            assert sess1.timeout_used == 4
            sess2.send(requ)
            assert sess2.timeout_used == 100

            with sess2.timeout_as(7):
                sess2.send(requ)
                assert sess2.timeout_used == 7
                sess1.send(requ)
                assert sess1.timeout_used == 4

    def test_no_context_var_memory_leak(self) -> None:
        def f() -> None:
            sess = MySession()
            with sess.timeout_as(1):
                sess.send(requ)
                with sess.timeout_as(2):
                    sess.send(requ)
                sess.send(requ)
            sess.send(requ)

        ctx = contextvars.Context()
        ctx.run(f)
        assert len(ctx) == 0
'''
