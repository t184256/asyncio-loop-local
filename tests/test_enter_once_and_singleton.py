# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test enter_once + singleton as an alternative to sticky_singleton_acm."""

import asyncio

import pytest
from common import CountingACM

from asyncio_loop_local._enter_once import enter_once
from asyncio_loop_local._singleton import singleton

_CountingACM = singleton()(CountingACM)


@pytest.mark.asyncio()
async def test_enter_once_plus_singleton() -> None:
    """Smoke-test enter_once + singleton used as sticky_singleton_acm."""
    # `async with SomeResource() as acm:` that lasts until the end of the loop
    acm0 = _CountingACM()
    assert (acm0.enters, acm0.exits) == (0, 0)

    acm = await enter_once(_CountingACM())
    assert (acm.enters, acm.exits) == (1, 0)
    a = await enter_once(_CountingACM())
    assert a is acm
    assert (acm.enters, acm.exits) == (1, 0)

    acmf = _CountingACM()
    assert (acmf.enters, acmf.exits) == (1, 0)


def test_two_loops_enter_once_plus_singleton() -> None:
    """Test enter_once + singleton with different loops."""

    async def test_entering_twice() -> CountingACM:
        acm = await enter_once(_CountingACM())
        assert (acm.enters, acm.exits) == (1, 0)
        a = await enter_once(_CountingACM())
        assert a is acm
        assert (acm.enters, acm.exits) == (1, 0)
        return acm

    l1 = asyncio.new_event_loop()
    acm = l1.run_until_complete(test_entering_twice())
    assert (acm.enters, acm.exits) == (1, 0)
    acm = l1.run_until_complete(test_entering_twice())
    assert (acm.enters, acm.exits) == (1, 0)
    l1.close()
    assert (acm.enters, acm.exits) == (1, 1)

    l2 = asyncio.new_event_loop()
    acm2 = l2.run_until_complete(test_entering_twice())
    assert acm2 is not acm
    assert (acm2.enters, acm2.exits) == (1, 0)
    l2.close()
    assert (acm2.enters, acm2.exits) == (1, 1)
