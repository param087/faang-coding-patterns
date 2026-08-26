"""Print FooBar Alternately — LeetCode 1115."""

from __future__ import annotations

import threading
from collections.abc import Callable

META = {
    "pattern": "concurrency",
    "symbol": "FooBar",
    "insight": "Two gates facing each other: each thread opens the other's gate and never its own, so neither can run twice in a row.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Two threads call `foo` and `bar`, each `n` times. Interleave them so the output
is `foobarfoobar...` — strict alternation, starting with `foo`.

Ask: is `foo` guaranteed to start first (yes, the output is fixed), and are the
two methods each called exactly once with their own loop inside (yes — the loop
lives in your method, not in the driver). That second one matters: you are
synchronising **inside** a loop, not once.
""",
        ),
        (
            "The insight",
            """
Two semaphores, `foo_gate` starting at **1** and `bar_gate` starting at **0**.
Each iteration a thread acquires its own gate, prints, and releases *the
other's*.

```
foo: acquire(foo_gate) -> print -> release(bar_gate)
bar: acquire(bar_gate) -> print -> release(foo_gate)
```

Exactly one permit is alive in the system at any moment and it is handed back
and forth. There is no shared counter, no `while` predicate, and nothing spins:
a blocked thread is descheduled by the OS.

The initial values *are* the specification — `foo_gate = 1` is the whole reason
`foo` goes first.
""",
        ),
        (
            "Why one lock is not enough",
            """
The reflex answer is a single `Lock` plus a boolean `foos_turn`:

```python
with self._lock:
    if self._foos_turn: ...
```

This is wrong, and not subtly. `foo` releases the lock at the end of its
iteration, loops round, and **reacquires it immediately** — it is already
running, while `bar` is still being woken by the scheduler. `foo` finds
`foos_turn` false, and now you either spin (burning a core, and on a build
without the GIL, with no guarantee the write is even visible) or you need a
condition variable anyway.

The fix is a `Condition` with a `while` loop, or — cleaner — the two-gate
version above, where a thread **cannot** proceed twice because it never
releases its own gate. Making the invariant structural rather than checked is
the judgement being assessed.
""",
        ),
    ],
}


class FooBar:
    def __init__(self, n: int) -> None:
        self.n = n
        # foo starts open, bar starts shut: the initial values encode the order.
        self._foo_gate = threading.Semaphore(1)
        self._bar_gate = threading.Semaphore(0)

    def foo(self, print_foo: Callable[[], None]) -> None:
        for _ in range(self.n):
            self._foo_gate.acquire()
            print_foo()
            self._bar_gate.release()  # opens the *other* gate, never its own

    def bar(self, print_bar: Callable[[], None]) -> None:
        for _ in range(self.n):
            self._bar_gate.acquire()
            print_bar()
            self._foo_gate.release()


def _run_once(n: int) -> list[str]:
    """One trial, with `bar` started first so a correct answer cannot be luck.

    The lambdas live here rather than in a loop body so each closes over *this*
    call's `output` (B023).
    """
    output: list[str] = []
    foobar = FooBar(n)
    bar_thread = threading.Thread(
        target=foobar.bar, args=(lambda: output.append("bar"),), daemon=True
    )
    foo_thread = threading.Thread(
        target=foobar.foo, args=(lambda: output.append("foo"),), daemon=True
    )
    bar_thread.start()
    foo_thread.start()
    for thread in (bar_thread, foo_thread):
        thread.join(timeout=5)
        assert not thread.is_alive(), f"deadlock at n={n}"
    return output


def check() -> None:
    for n in (0, 1, 2, 5, 20):
        expected = ["foo", "bar"] * n
        # Repeat: a single pass could be scheduling luck rather than correctness.
        for _ in range(15):
            assert _run_once(n) == expected
