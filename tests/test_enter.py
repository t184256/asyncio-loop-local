# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local.enter."""

import asyncio

import pytest
from common import CountingACM

import asyncio_loop_local


@pytest.mark.asyncio()
async def test_enter() -> None:
    """Smoke-test enter."""
    # `async with SomeResource() as acm:` that lasts until the end of the loop
    acm = await asyncio_loop_local.enter(CountingACM())
    assert (acm.enters, acm.exits) == (1, 0)
    await asyncio_loop_local.enter(acm)
    assert (acm.enters, acm.exits) == (2, 0)


def test_two_loops_enter() -> None:
    """Test enter with different event loops."""
    acm = CountingACM()

    async def test_entering(initial_enters: int, initial_exits: int) -> None:
        assert (acm.enters, acm.exits) == (initial_enters, initial_exits)
        await asyncio_loop_local.enter(acm)
        assert (acm.enters, acm.exits) == (initial_enters + 1, initial_exits)
        await asyncio_loop_local.enter(acm)
        assert (acm.enters, acm.exits) == (initial_enters + 2, initial_exits)

    l1 = asyncio.new_event_loop()
    assert (acm.enters, acm.exits) == (0, 0)
    l1.run_until_complete(test_entering(0, 0))
    l1.run_until_complete(test_entering(2, 0))
    assert (acm.enters, acm.exits) == (4, 0)
    l1.close()
    assert (acm.enters, acm.exits) == (4, 4)

    l2 = asyncio.new_event_loop()
    assert (acm.enters, acm.exits) == (4, 4)
    l2.run_until_complete(test_entering(4, 4))
    l2.run_until_complete(test_entering(6, 4))
    assert (acm.enters, acm.exits) == (8, 4)
    l2.close()
    assert (acm.enters, acm.exits) == (8, 8)
