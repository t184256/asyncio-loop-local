# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Shared code between tests."""

import asyncio
import types
import typing


class CountingACM:
    """Asynchronous context manager tracking how many times it's entered."""

    enters: int
    exits: int

    def __init__(self: typing.Self) -> None:
        """Initialize CountingACM."""
        self.enters = self.exits = 0

    async def __aenter__(self: typing.Self) -> typing.Self:
        await asyncio.sleep(0)  # give concurrency bugs a chance to manifest
        self.enters += 1
        await asyncio.sleep(0)
        return self

    async def __aexit__(
        self: typing.Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        await asyncio.sleep(0)
        self.exits += 1
        await asyncio.sleep(0)
        return None
