# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Enter context once, exit with the loop."""

import contextlib
import typing

import asyncio_loop_local._enter

_T = typing.TypeVar('_T')
_ACM = contextlib.AbstractAsyncContextManager


enter_once_sentinel = object()


async def enter_once(acm: _ACM[_T]) -> _T:
    ls = asyncio_loop_local._storage.storage()  # noqa: SLF001
    c: dict[_ACM[_T], _T]
    try:
        c = ls[enter_once_sentinel]
    except KeyError:
        c = ls[enter_once_sentinel] = {}

    try:
        return c[acm]
    except KeyError:
        pass
    c[acm] = ret = await asyncio_loop_local._enter.enter(acm)  # noqa: SLF001
    return ret


__all__ = ['enter_once']
