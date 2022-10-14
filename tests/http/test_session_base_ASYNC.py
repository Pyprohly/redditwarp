
from __future__ import annotations
from typing import Optional

# import asyncio
# import contextvars

# import pytest

from redditwarp.http.session_base_ASYNC import SessionBase
from redditwarp.http.response import Response
from redditwarp.http.request import Request

class MySession(SessionBase):
    def __init__(self) -> None:
        super().__init__()
        self.timeout = 100
        # self.timeout_used: float = 0

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        # self.timeout_used = self._get_effective_timeout_value(timeout)
        return Response(200, {}, b'')

requ = Request('', '', params={}, headers={}, payload=None)

# Unused idea for now
'''
class TestTimeoutAsMethod:
    @pytest.mark.asyncio
    async def test_basics(self) -> None:
        sess = MySession()
        with sess.timeout_as(3):
            await sess.send(requ)
            assert sess.timeout_used == 3
            await sess.send(requ)
            assert sess.timeout_used == 3
        await sess.send(requ)
        assert sess.timeout_used == 100

        sess.timeout_as(9)
        await sess.send(requ)
        assert sess.timeout_used == 100

    @pytest.mark.asyncio
    async def test_timeout_precedence(self) -> None:
        sess = MySession()
        assert sess.timeout_used == 0

        await sess.send(requ)
        assert sess.timeout_used == 100

        await sess.send(requ, timeout=200)
        assert sess.timeout_used == 200

        with sess.timeout_as(300):
            await sess.send(requ, timeout=200)
        assert sess.timeout_used == 300

    @pytest.mark.asyncio
    async def test_nested(self) -> None:
        sess = MySession()
        with sess.timeout_as(1):
            await sess.send(requ)
            assert sess.timeout_used == 1

            with sess.timeout_as(2):
                await sess.send(requ)
                assert sess.timeout_used == 2

            await sess.send(requ)
            assert sess.timeout_used == 1

        await sess.send(requ)
        assert sess.timeout_used == 100

    @pytest.mark.asyncio
    async def test_reuse(self) -> None:
        sess = MySession()
        timeout_context = sess.timeout_as(5)
        with timeout_context:
            await sess.send(requ)
            assert sess.timeout_used == 5

        await sess.send(requ)
        assert sess.timeout_used == 100

        with timeout_context:
            await sess.send(requ)
            assert sess.timeout_used == 5

    @pytest.mark.asyncio
    async def test_reentrancy(self) -> None:
        sess = MySession()
        timeout_context = sess.timeout_as(6)
        with timeout_context:
            await sess.send(requ)
            assert sess.timeout_used == 6

            with timeout_context:
                await sess.send(requ)
                assert sess.timeout_used == 6

            await sess.send(requ)
            assert sess.timeout_used == 6

        await sess.send(requ)
        assert sess.timeout_used == 100

    @pytest.mark.asyncio
    async def test_other_instances_arent_affected(self) -> None:
        sess1 = MySession()
        sess2 = MySession()

        with sess1.timeout_as(4):
            await sess1.send(requ)
            assert sess1.timeout_used == 4
            await sess2.send(requ)
            assert sess2.timeout_used == 100

            with sess2.timeout_as(7):
                await sess2.send(requ)
                assert sess2.timeout_used == 7
                await sess1.send(requ)
                assert sess1.timeout_used == 4

    @pytest.mark.asyncio
    async def test_no_context_var_memory_leak(self) -> None:
        async def f() -> None:
            sess = MySession()
            with sess.timeout_as(1):
                await sess.send(requ)
                with sess.timeout_as(2):
                    await sess.send(requ)
                await sess.send(requ)
            await sess.send(requ)

        ctx = contextvars.Context()
        await ctx.run(asyncio.create_task, f())
        assert len(ctx) == 0

class TestTimeoutAsMethodAsync:
    @pytest.mark.asyncio
    async def test_other_tasks_arent_affected(self) -> None:
        sess = MySession()
        async def coro(x: int) -> None:
            with sess.timeout_as(x):
                await asyncio.sleep(0)
                await sess.send(requ)
                assert sess.timeout_used == x
                await asyncio.sleep(0)

        coros = [coro(i) for i in range(100)]
        await asyncio.gather(*coros)
'''
