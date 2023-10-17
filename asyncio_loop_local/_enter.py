# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Enter context now, exit when the loop shuts down."""

import contextlib
import typing

import asyncio_loop_local._atexit

_T = typing.TypeVar('_T')
_ACM = contextlib.AbstractAsyncContextManager


async def enter(acm: _ACM[_T]) -> _T:
    ret = await acm.__aenter__()

    async def aexit_hook() -> None:
        await acm.__aexit__(None, None, None)

    asyncio_loop_local._atexit._register(aexit_hook())  # noqa: SLF001

    return ret


__all__ = ['enter']
