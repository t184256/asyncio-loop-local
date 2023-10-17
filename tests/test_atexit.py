# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local._atexit hooks."""

import asyncio

import pytest

import asyncio_loop_local._atexit


def test_atexit() -> None:
    """Test atexit functionality."""
    log = []

    async def hook1() -> None:
        await asyncio.sleep(0)
        log.append(1)

    async def hook2() -> None:
        await asyncio.sleep(0)
        log.append(2)

    async def main() -> None:
        asyncio_loop_local._atexit._register(hook1())  # noqa: SLF001
        asyncio_loop_local._atexit._register(hook2())  # noqa: SLF001
        await asyncio.sleep(0)
        log.append(0)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()

    assert log == [0, 2, 1]


@pytest.mark.asyncio()
async def test_no_atexit() -> None:
    """Test a corner case of triggering `_fire` without registering hooks."""
    await asyncio_loop_local._atexit._fire()  # noqa: SLF001
