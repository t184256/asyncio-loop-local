# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local.singleton."""

import asyncio
import types
import typing

import pytest

import asyncio_loop_local


class ActionLog:
    """A helper testing class that stores what happens."""

    log: list[str]

    def __init__(self: typing.Self) -> None:  # noqa: D107
        self.log = []

    def log_sync(self: typing.Self, a: str) -> None:  # noqa: D102
        self.log.append(a)

    async def __call__(self: typing.Self, a: str) -> None:  # noqa: D102
        self.log.append(a)

    def ensure(self: typing.Self, *log: str) -> None:  # noqa: D102
        assert tuple(self.log) == log


###


@asyncio_loop_local.singleton()
class SomeResource:
    """A helper testing class that logs enters/exits, to test singleton on."""

    def __init__(self: typing.Self, log: ActionLog, name: str = 's') -> None:
        """Initialize and log that."""
        self.log = log
        self.name = name
        self.log.log_sync(f'{self.name} init')

    async def __aenter__(self: typing.Self) -> typing.Self:
        """Enter and log that."""
        await self.log(f'{self.name} enter')
        return self

    async def __aexit__(
        self: typing.Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        """Exit and log that."""
        await self.log(f'{self.name} exit')
        return None


@pytest.mark.asyncio()
async def test_smoke_singleton_class_decorator() -> None:
    """Test singleton usage as class decorator."""
    log = ActionLog()
    async with SomeResource(log) as sr1:
        await log('1')
    log.ensure('s init', 's enter', '1', 's exit')

    async with SomeResource(log) as sr2:
        await log('2')
    res1 = ('s init', 's enter', '1', 's exit', 's enter', '2', 's exit')
    log.ensure(*res1)

    async with SomeResource(log, name='x') as sr3:
        await log('3')
    async with SomeResource(log, name='x') as sr4:
        await log('4')
    res2 = ('x init', 'x enter', '3', 'x exit', 'x enter', '4', 'x exit')
    log.ensure(*res1, *res2)

    assert sr1 is sr2
    assert sr3 is sr4
    assert sr1 is not sr3


def test_two_loops_singleton_class_decorator() -> None:
    """Test singleton usage as class decorator in separate loops."""
    log = ActionLog()

    async def do() -> SomeResource:
        async with SomeResource(log, name='x') as sr:
            return sr

    async def do_twice() -> SomeResource:
        sr_a = await do()
        sr_b = await do()
        assert sr_a is sr_b
        return sr_a

    l1 = asyncio.new_event_loop()
    sr1 = l1.run_until_complete(do_twice())
    log.ensure('x init', 'x enter', 'x exit', 'x enter', 'x exit')

    l2 = asyncio.new_event_loop()
    sr2 = l2.run_until_complete(do_twice())
    log.ensure(*(('x init', 'x enter', 'x exit', 'x enter', 'x exit') * 2))

    assert sr1 is not sr2

    l1.close()
    l2.close()


###


@asyncio_loop_local.singleton()
def func_maker(log: ActionLog, x: int) -> typing.Callable[[], None]:
    """A function to test singleton on."""  # noqa: D401
    log.log_sync(f'made {x}-maker')

    def func() -> None:
        log.log_sync(str(x))

    return func


@pytest.mark.asyncio()
async def test_smoke_singleton_function_decorator() -> None:
    """Test singleton usage as sync function decorator."""
    log = ActionLog()

    sf1_1 = func_maker(log, 1)
    sf1_1()
    log.ensure('made 1-maker', '1')

    sf1_2 = func_maker(log, 1)
    assert sf1_1 is sf1_2
    sf1_2()
    log.ensure('made 1-maker', '1', '1')

    sf2 = func_maker(log, 2)
    assert sf1_1 is not sf2
    assert sf1_2 is not sf2
    sf2()
    log.ensure('made 1-maker', '1', '1', 'made 2-maker', '2')


###


@asyncio_loop_local.singleton()
async def coro(x: int) -> None:
    """A coroutine to test singleton on."""  # noqa: D401
    asyncio_loop_local.storage()['list'].append(x)
    await asyncio.sleep(0.001)


@pytest.mark.asyncio()
async def test_smoke_singleton_coroutine_decorator() -> None:
    """Test singleton usage as an async coroutine decorator."""
    asyncio_loop_local.storage()['list'] = []
    assert coro(0) is coro(0)  # singleton-ing makes ids match
    coros = []
    for i in range(7):
        coros.extend([coro(i), coro(i)])  # 0, 0, 1, 1, 2, 2, ...
    await asyncio.gather(*coros[:6])  # run 0, 1, 2; id duplicates don't run
    assert sorted(asyncio_loop_local.storage()['list']) == [0, 1, 2]


###


@asyncio_loop_local.singleton
async def coro2(x: int) -> None:
    """A coroutine to test singleton on (no brackets)."""  # noqa: D401
    asyncio_loop_local.storage()['list'].append(x)
    await asyncio.sleep(0.001)


@pytest.mark.asyncio()
async def test_smoke_singleton_coroutine_nb_decorator() -> None:
    """Test singleton usage as an async coroutine decorator (no brackets)."""
    asyncio_loop_local.storage()['list'] = []
    assert coro2(0) is coro2(0)  # singleton-ing makes ids match
    coros = []
    for i in range(7):
        coros.extend([coro2(i), coro2(i)])  # 0, 0, 1, 1, 2, 2, ...
    await asyncio.gather(*coros[:6])  # run 0, 1, 2; id duplicates don't run
    assert sorted(asyncio_loop_local.storage()['list']) == [0, 1, 2]
