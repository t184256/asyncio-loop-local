# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local.sticky_singleton_acm."""

import asyncio

import pytest
from common import CountingACM

from asyncio_loop_local._sticky_singleton_acm import sticky_singleton_acm

_CountingACM = sticky_singleton_acm(CountingACM)


@pytest.mark.asyncio()
async def test_enter_sticky_singleton_acm() -> None:
    """Smoke-test sticky_singleton_acm."""
    # `async with CountingACM() as acm:` that lasts until the end of the loop
    async with _CountingACM() as acm:
        assert (acm.enters, acm.exits) == (1, 0)
        async with _CountingACM() as a:
            assert a is acm
            assert (acm.enters, acm.exits) == (1, 0)
        assert (acm.enters, acm.exits) == (1, 0)
    async with _CountingACM() as acm:
        assert (acm.enters, acm.exits) == (1, 0)
    assert (acm.enters, acm.exits) == (1, 0)


def test_two_loops_sticky_singleton_acm() -> None:
    """Test sticky_singleton_acm with several event loops."""

    async def test_entering_twice() -> CountingACM:
        async with _CountingACM() as acm:
            assert (acm.enters, acm.exits) == (1, 0)
            async with _CountingACM() as a:
                assert a is acm
                assert (acm.enters, acm.exits) == (1, 0)
            assert (acm.enters, acm.exits) == (1, 0)
        async with _CountingACM() as acm:
            assert (acm.enters, acm.exits) == (1, 0)
        assert (acm.enters, acm.exits) == (1, 0)
        return acm

    l1 = asyncio.new_event_loop()
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
