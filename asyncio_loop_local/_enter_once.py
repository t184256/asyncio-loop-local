# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Enter context once, exit with the loop."""

import asyncio
import contextlib
import typing

import asyncio_loop_local._enter

_T = typing.TypeVar('_T')
_ACM = contextlib.AbstractAsyncContextManager


enter_once_sentinel = object()


class _LockingDict(asyncio.Lock, dict[_ACM[_T], _T]):
    pass


async def enter_once(acm: _ACM[_T]) -> _T:
    ls = asyncio_loop_local._storage.storage()  # noqa: SLF001
    c: _LockingDict[_T]
    try:
        c = ls[enter_once_sentinel]
    except KeyError:
        c = ls[enter_once_sentinel] = _LockingDict()

    async with c:
        try:
            return c[acm]
        except KeyError:
            pass
        c[acm] = r = await asyncio_loop_local._enter.enter(acm)  # noqa: SLF001
        return r


__all__ = ['enter_once']
