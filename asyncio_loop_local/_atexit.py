# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Set atexit hooks to fire at the end of the as."""

import asyncio
import typing

import asyncio_loop_local._storage

atexit_key_sentinel = object()


def _register(hook: typing.Awaitable[None]) -> None:
    ls = asyncio_loop_local._storage.storage()  # noqa: SLF001
    try:
        hooks = ls[atexit_key_sentinel]
    except KeyError:
        hooks = ls[atexit_key_sentinel] = []
        loop = asyncio.get_running_loop()
        original_close = loop.close

        def extended_close() -> None:
            if not loop.is_closed():
                loop.run_until_complete(_fire())
            return original_close()

        loop.close = extended_close  # type: ignore[method-assign]

    hooks.append(hook)


async def _fire() -> None:
    ls = asyncio_loop_local._storage.storage()  # noqa: SLF001
    try:
        hooks = ls[atexit_key_sentinel]
    except KeyError:
        return
    for hook in hooks[::-1]:
        await hook
    del ls[atexit_key_sentinel]


__all__ = ['_register', '_fire']
