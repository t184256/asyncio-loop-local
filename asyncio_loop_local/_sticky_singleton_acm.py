# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0

"""Sticky singleton async context manager.

If you got some `Session` async context manager factory function, and decorate
it with `sticky_singleton_acm`, the resulting object:

* gives you the same `Session` on aentering
* only aexits it at the end of the event loop
"""

import contextlib
import typing

from asyncio_loop_local._singleton import singleton
from asyncio_loop_local._sticky_acm import sticky_acm

_P = typing.ParamSpec('_P')
_T = typing.TypeVar('_T')
_ACM = contextlib.AbstractAsyncContextManager


def sticky_singleton_acm(
    acm_func: typing.Callable[_P, _ACM[_T]],
) -> typing.Callable[_P, _ACM[_T]]:
    def mk_sticky_singleton_acm(
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _ACM[_T]:
        s_acm_func = singleton()(acm_func)
        return sticky_acm(s_acm_func(*args, **kwargs))

    return mk_sticky_singleton_acm


__all__ = ['sticky_singleton_acm']
