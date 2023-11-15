# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Test asyncio_loop_local.storage."""

import asyncio
import typing

import pytest

import asyncio_loop_local
from asyncio_loop_local._storage import _loop_local_storages


@pytest.mark.asyncio()
async def test_smoke() -> None:
    """Smoke-test loop-local storage."""
    lls = asyncio_loop_local.storage()
    assert not lls
    lls['x'] = 'y'
    assert lls == {'x': 'y'}
    assert asyncio_loop_local.storage() is lls


def test_sync_fail() -> None:
    """Test loop-local storage without an event loop running."""
    with pytest.raises(RuntimeError) as ex:
        asyncio_loop_local.storage()
    assert str(ex.value) == 'no running event loop'


def test_two_loops() -> None:
    """Test loop-local storage with different loops."""

    async def ls_update(**kwargs: typing.Any) -> None:  # noqa: ANN401
        asyncio_loop_local.storage().update(**kwargs)

    async def ls_assert(**kwargs: typing.Any) -> None:  # noqa: ANN401
        assert asyncio_loop_local.storage() == kwargs

    async def ls_test(**kwargs: typing.Any) -> None:  # noqa: ANN401
        await ls_update(**kwargs)
        await ls_assert(**kwargs)

    l1 = asyncio.new_event_loop()
    l1.run_until_complete(ls_test(x=0))

    l2 = asyncio.new_event_loop()
    l2.run_until_complete(ls_test(y=True))

    l1.close()
    l2.close()

    assert l1 in _loop_local_storages
    assert any(r == {'x': 0} for r in _loop_local_storages.values())
    assert l2 in _loop_local_storages
    assert any(r == {'y': True} for r in _loop_local_storages.values())

    del l1
    assert not any(r == {'x': 0} for r in _loop_local_storages.values())
    assert l2 in _loop_local_storages
    assert any(r == {'y': True} for r in _loop_local_storages.values())

    del l2
    assert not any(r == {'x': 0} for r in _loop_local_storages.values())
    assert not any(r == {'y': True} for r in _loop_local_storages.values())


@pytest.mark.asyncio()
async def test_locking() -> None:
    """Does not test functionality, just a recommended pattern."""

    async def ls_grow_list() -> None:
        ls = asyncio_loop_local.storage()
        async with ls['list_lock']:
            if 'list' not in ls:
                await asyncio.sleep(0.001)  # race condition intensificator
                ls['list'] = []
            ls['list'].append(None)

    asyncio_loop_local.storage()['list_lock'] = asyncio.Lock()
    await asyncio.gather(*(ls_grow_list() for _ in range(100)))
    assert asyncio_loop_local.storage()['list'] == [None] * 100
