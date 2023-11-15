# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Enter context only once using `async with`, exit with the loop."""

import asyncio
import contextlib
import types
import typing

import asyncio_loop_local._atexit
import asyncio_loop_local._enter
import asyncio_loop_local._storage

_T = typing.TypeVar('_T')
_ACM = contextlib.AbstractAsyncContextManager

sticky_acm_sentinel = object()


def sticky_acm(acm: _ACM[_T]) -> _ACM[_T]:
    ls = asyncio_loop_local._storage.storage()  # noqa: SLF001
    try:
        c = ls[sticky_acm_sentinel]
    except KeyError:
        c = ls[sticky_acm_sentinel] = {}

    try:
        return typing.cast(_ACM[_T], c[acm])
    except KeyError:
        pass

    class StickyACM:
        _entered: bool
        _val: _T | None
        _lock: asyncio.Lock

        def __init__(self: typing.Self) -> None:
            self._entered = False
            self._val = None
            self._lock = asyncio.Lock()

        async def __aenter__(self: typing.Self) -> _T:
            if self._entered:
                return typing.cast(_T, self._val)
            async with self._lock:
                if self._entered:
                    return typing.cast(_T, self._val)

                r = await asyncio_loop_local._enter.enter(acm)  # noqa: SLF001
                self._entered = True
                self._val = r
            return r

        @staticmethod
        async def __aexit__(  # noqa: PYI036
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,  # noqa: PYI036
            exc_tb: types.TracebackType | None,  # noqa: PYI036
        ) -> None:
            return None

    ret = c[acm] = StickyACM()
    return ret


__all__ = ['sticky_acm']
