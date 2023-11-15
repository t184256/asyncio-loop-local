# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local.sticky_acm __aexit__ deferrence."""

import asyncio

import pytest
from common import CountingACM

from asyncio_loop_local._sticky_acm import sticky_acm


@pytest.mark.asyncio()
async def test_sticky_acm() -> None:
    """Smoke-test sticky_acm."""
    acm = CountingACM()
    assert (acm.enters, acm.exits) == (0, 0)
    async with sticky_acm(acm) as _acm:
        assert acm is _acm
        assert (acm.enters, acm.exits) == (1, 0)
        async with sticky_acm(acm) as _acm:
            assert acm is _acm
            assert (acm.enters, acm.exits) == (1, 0)
        assert (acm.enters, acm.exits) == (1, 0)
    assert (acm.enters, acm.exits) == (1, 0)
    async with sticky_acm(acm):
        assert (acm.enters, acm.exits) == (1, 0)
    assert (acm.enters, acm.exits) == (1, 0)


def test_two_loops_sticky_acm() -> None:
    """Test sticky_acm with different loops."""
    acm = CountingACM()
    assert (acm.enters, acm.exits) == (0, 0)

    async def poke(initial: int) -> None:
        assert (acm.enters, acm.exits) == (initial, 0)
        async with sticky_acm(acm) as _acm:
            assert acm is _acm
            assert (acm.enters, acm.exits) == (1, 0)
            async with sticky_acm(acm) as _acm:
                assert acm is _acm
                assert (acm.enters, acm.exits) == (1, 0)
            assert (acm.enters, acm.exits) == (1, 0)
        assert (acm.enters, acm.exits) == (1, 0)
        async with sticky_acm(acm):
            assert (acm.enters, acm.exits) == (1, 0)
        assert (acm.enters, acm.exits) == (1, 0)

        async with sticky_acm(acm) as _acm:
            assert acm is _acm
            assert (acm.enters, acm.exits) == (1, 0)
        assert (acm.enters, acm.exits) == (1, 0)

    l1 = asyncio.new_event_loop()
    assert (acm.enters, acm.exits) == (0, 0)
    l1.run_until_complete(poke(initial=0))
    l1.run_until_complete(poke(initial=1))
    assert (acm.enters, acm.exits) == (1, 0)
    l1.close()
    assert (acm.enters, acm.exits) == (1, 1)

    async def poke2(initial: int = 0) -> None:
        assert (acm.enters, acm.exits) == (1 + initial, 1)
        async with sticky_acm(acm) as _acm:
            assert acm is _acm
            assert (acm.enters, acm.exits) == (2, 1)
        assert (acm.enters, acm.exits) == (2, 1)

    l2 = asyncio.new_event_loop()
    assert (acm.enters, acm.exits) == (1, 1)
    l2.run_until_complete(poke2(initial=0))
    assert (acm.enters, acm.exits) == (2, 1)
    l2.run_until_complete(poke2(initial=1))
    assert (acm.enters, acm.exits) == (2, 1)
    l2.close()
    assert (acm.enters, acm.exits) == (2, 2)


@pytest.mark.asyncio()
async def test_enter_once_parallel() -> None:
    """Test enter_once executing in parallel."""
    acm = CountingACM()

    async def enter_exit() -> None:
        async with sticky_acm(acm) as _acm:
            assert acm is _acm

    await asyncio.gather(*[enter_exit() for _ in range(7)])
    assert (acm.enters, acm.exits) == (1, 0)
