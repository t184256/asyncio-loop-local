# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local.enter_once."""

import asyncio

import pytest
from common import CountingACM

import asyncio_loop_local


@pytest.mark.asyncio()
async def test_enter_once() -> None:
    """Smoke-test enter_once."""
    # `async with SomeResource() as acm:` that lasts until the end of the loop
    acm = await asyncio_loop_local.enter_once(CountingACM())
    assert (acm.enters, acm.exits) == (1, 0)
    await asyncio_loop_local.enter_once(acm)
    assert (acm.enters, acm.exits) == (1, 0)


def test_two_loops_enter_once() -> None:
    """Test enter_once with different event loops."""
    acm = CountingACM()

    async def test_entering_first_loop() -> None:
        assert (acm.enters, acm.exits) == (0, 0)
        await asyncio_loop_local.enter_once(acm)
        assert (acm.enters, acm.exits) == (1, 0)
        await asyncio_loop_local.enter_once(acm)
        assert (acm.enters, acm.exits) == (1, 0)

    l1 = asyncio.new_event_loop()
    assert (acm.enters, acm.exits) == (0, 0)
    l1.run_until_complete(test_entering_first_loop())
    assert (acm.enters, acm.exits) == (1, 0)
    l1.close()
    assert (acm.enters, acm.exits) == (1, 1)

    async def test_entering_second_loop() -> None:
        assert (acm.enters, acm.exits) == (1, 1)
        await asyncio_loop_local.enter_once(acm)
        assert (acm.enters, acm.exits) == (2, 1)
        await asyncio_loop_local.enter_once(acm)
        assert (acm.enters, acm.exits) == (2, 1)

    l2 = asyncio.new_event_loop()
    assert (acm.enters, acm.exits) == (1, 1)
    l2.run_until_complete(test_entering_second_loop())
    assert (acm.enters, acm.exits) == (2, 1)
    l2.close()
    assert (acm.enters, acm.exits) == (2, 2)


@pytest.mark.asyncio()
async def test_enter_once_parallel() -> None:
    """Test enter_once executing in parallel."""
    acm = CountingACM()
    await asyncio.gather(
        *[asyncio_loop_local.enter_once(acm) for _ in range(7)],
    )
    assert (acm.enters, acm.exits) == (1, 0)
