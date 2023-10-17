# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""asyncio-loop-local storage. Like thread-local, but for asyncio loops."""

import asyncio
import typing
import weakref

# globals
_loop_local_storages: weakref.WeakKeyDictionary[
    asyncio.AbstractEventLoop,
    'LoopLocalStorage',
] = weakref.WeakKeyDictionary()


class LoopLocalStorage(dict[typing.Any, typing.Any]):
    """asyncio-loop-local storage. Like thread-local, but for asyncio loops."""


def storage() -> LoopLocalStorage:
    loop = asyncio.get_running_loop()
    try:
        return _loop_local_storages[loop]
    except KeyError:
        pass
    new_ls = LoopLocalStorage()
    _loop_local_storages[loop] = new_ls
    return new_ls


__all__ = ['storage']
