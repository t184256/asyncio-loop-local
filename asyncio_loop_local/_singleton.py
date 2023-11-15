# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Initialize something once per loop and share it, clean up at the end."""

import functools
import typing

import asyncio_loop_local._storage

_P = typing.ParamSpec('_P')
_T = typing.TypeVar('_T')
_Decorator = typing.Callable[
    [typing.Callable[_P, _T]],
    typing.Callable[_P, _T],
]


class SingletonCache(
    dict[
        tuple[
            typing.Callable[_P, _T],
            _P.args,
            tuple[tuple[str, typing.Any], ...],  # should be _P.kwargs, but uh
        ],
        _T,
    ],
):
    pass  # with the type like this, who needs a class body?


singleton_cache_key_sentinel = object()


@typing.overload  # for decorating with singleton()
def singleton(
    callable_: None = None,
) -> typing.Callable[
    [typing.Callable[_P, _T]],
    typing.Callable[_P, _T],
]: ...  # overload


@typing.overload  # for decorating with singleton
def singleton(
    callable_: typing.Callable[_P, _T],
) -> typing.Callable[_P, _T]: ...  # overload


# I want to be able to later extend it with parameters, so, two forms
def singleton(
    callable_: typing.Callable[_P, _T] | None = None,
) -> typing.Callable[_P, _T] | _Decorator[_P, _T]:
    if callable_ is None:
        return _singletonize
    return _singletonize(callable_)


def _singletonize(f: typing.Callable[_P, _T]) -> typing.Callable[_P, _T]:
    @functools.wraps(f)
    def reuse_sync(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        # sync version wrapping a regular function, no locking required
        ls = asyncio_loop_local._storage.storage()  # noqa: SLF001
        try:
            sc = ls[singleton_cache_key_sentinel]
        except KeyError:
            sc = ls[singleton_cache_key_sentinel] = SingletonCache()
        key = f, args, tuple(kwargs.items())
        try:
            return typing.cast(_T, sc[key])
        except KeyError:
            pass
        res = sc[key] = f(*args, **kwargs)
        return res

    return reuse_sync


__all__ = ['singleton']
