# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""asyncio-loop-local.

asyncio-loop-local storage, singletons, sticky async context managers...
Init that pool once and reuse it!
"""

from asyncio_loop_local._enter import enter
from asyncio_loop_local._enter_once import enter_once
from asyncio_loop_local._singleton import singleton
from asyncio_loop_local._sticky_acm import sticky_acm
from asyncio_loop_local._sticky_singleton_acm import sticky_singleton_acm
from asyncio_loop_local._storage import storage

__all__ = [
    'enter',
    'enter_once',
    'singleton',
    'sticky_acm',
    'sticky_singleton_acm',
    'storage',
]
