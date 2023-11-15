# asyncio-loop-local

asyncio-loop-local storage, singletons and deferred __aexit__'s. Init that pool once and reuse it!


## why have loop-local things

Suppose you have some async context manager, like `aiohttp.ClientSession`:

```
async with aiohttp.ClientSession() as session:
    async with session.get('http://httpbin.org/get') as resp:
        print(await resp.text())
```

But the docs tell you: "don't create a session per request".
So, you need to reuse it somehow, and this means you need to init it somewhere
and then either pass it around all the code that might need it,
or... use global variables? There must be a better way.


## `sticky_singleton_acm`

The all-in-one solution to this is:

```
_ClientSession = asyncio_loop_local.sticky_singleton_acm(ClientSession)

...

async _ClientSession() as session:
    async with session.get('http://httpbin.org/get') as resp:
        print(await resp.text())
```

The wrapper gives you

* the same `ClientSession` for every combination of parameters passed to it
  (singleton)
* that doesn't `__aexit__` when the block is over,
  only when the async event loop is closed
  (sticky ACM)


## `enter_once` + `singleton`

Those willing to save up a level of indentation
(after all, de-denting is a no-op as `__aexit__`'ing effect is deferred anyway)
might be interested in
combining two simpler primitives to the same effect:

```
_ClientSession = asyncio_loop_local.singleton(ClientSession)

...

session = await asyncio_loop_local.enter_once(_ClientSession())
async with session.get('http://httpbin.org/get') as resp:
    print(await resp.text())
```


## `singleton`

Decorate your callable that generates something,
and the returned value will be cached per async loop
(and per passed parameters).

```
_ClientSession = asyncio_loop_local.singleton(ClientSession)

_ClientSession() is _ClientSession()  # as long you're in the same event loop
```


## `enter_once`

Invoke `__anter__` of an asynchronous context manager now,
defer `__aexit__` to the end of the event loop.
Repeated attempts to `enter_once` on the same object will do nothing.

```
session = await asyncio_loop_local.enter_once(ClientSession())
...
# __aexit__ will be executed at the end of the event loop
```


## `sticky_acm`

Wrap an asynchronous context manager.
`__anter__` just proxies the original context manager's `__aenter__`,
`__aexit__` does nothing and is deferred to end of the event loop.
It's like `enter_once`, but in a form to use with `async with`.


```
cs = asyncio_loop_local.sticky_acm(ClientSession())
async with cs:  # __aenter__'s
    ...
# __aexit__ will be executed at the end of the event loop
```


## `enter`

Invoke `__anter__` of an asynchronous context manager now,
defer `__aexit__` to the end of the event loop.

```
session = await asyncio_loop_local.enter_once(ClientSession())
...
# __aexit__ will be executed at the end of the event loop
```


## `storage`

Async-loop-local storage. Like thread-local, but loop-local.
All the hacks above are built up on it.

```
alls = asyncio_loop_local._storage.storage()  # gives a loop-associated dict
alls['purpose'] = ('whatever', {'you': 'want'})
```

If you wanna use locking, consider this:

```
class LockingDict(asyncio.Lock, dict): pass
alls['careful'] = LockingDict()
with alls['careful'] as d:
   d['a'] = 'b'
```


## `_atexit`

There's also an async-loop-local atexit hook implementation.
It's private so far until some interest is expressed.
