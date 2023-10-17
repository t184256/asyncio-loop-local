# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Shared code between tests."""

import pytest
from common import CountingACM


@pytest.mark.asyncio()
async def test_counting_acm() -> None:
    """Smoke-test CountingACM functionality."""
    acm = CountingACM()
    assert (acm.enters, acm.exits) == (0, 0)
    async with acm:
        assert (acm.enters, acm.exits) == (1, 0)
        async with acm:
            assert (acm.enters, acm.exits) == (2, 0)
        assert (acm.enters, acm.exits) == (2, 1)
    assert (acm.enters, acm.exits) == (2, 2)
