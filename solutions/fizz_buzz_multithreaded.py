"""Fizz Buzz Multithreaded — LeetCode 1195."""

from __future__ import annotations

import threading
from collections.abc import Callable

META = {
    "pattern": "concurrency",
    "symbol": "FizzBuzz",
    "insight": "Four threads, one shared counter: each waits on a condition until the counter is its kind of number, prints, bumps it and wakes everyone.",
    "time": "O(n) prints, O(4n) wake-ups",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Four threads share one instance and one implicit counter running `1..n`.
`fizz` handles multiples of 3, `buzz` multiples of 5, `fizzbuzz` multiples of
15, `number` everything else. The concatenated output must be exactly ordinary
FizzBuzz.

Ask whether `n` is known up front (yes, it is a constructor argument) — that is
what lets every thread compute its own termination condition instead of needing
a poison pill.
""",
        ),
        (
            "The insight",
            """
Four threads cannot pass a baton in a fixed cycle, because which thread runs
next depends on the *value* of the counter, not on a rotation. So this is a
**condition variable**, not a chain of semaphores: one shared counter, one
`Condition`, and each thread waits until the counter is its kind of number.

Every one of the four bodies is the same shape, so write it once:

```python
while True:
    with self._condition:
        while self._current <= self.n and not wants(self._current):
            self._condition.wait()
        if self._current > self.n:
            return
        emit(self._current)
        self._current += 1
        self._condition.notify_all()
```

Four one-line predicates and the whole problem collapses. In an interview,
factoring that shared `_run` out is worth more than the synchronisation itself:
it turns four near-identical bodies you will typo into one you can reason about.
""",
        ),
        (
            "The two words that decide it",
            """
**`while`, not `if`.** A wake-up means "the state may have changed", not "it is
your turn". Every `notify_all` wakes three threads and at most one of them has
a true predicate; with an `if`, the other two fall through and print out of
turn. It is also the only defence against spurious wake-ups, which POSIX
explicitly permits.

**`notify_all`, not `notify`.** Four waiters, exactly one predicate true, so a
single `notify` picks a thread that can actually proceed at best one time in
four. When it picks wrong, that thread rechecks, goes straight back to
`wait()`, and the signal is gone — nobody is left holding a reason to wake
anyone. Swapping the two calls in the code below hangs before it reaches
`n = 5`. This is the same lost-wakeup shape as the bounded blocking queue, and
the same two escapes: `notify_all`, or one condition variable per predicate
(here that would be four, which is why `notify_all` wins).

**And the one people expect to matter but does not.** There is no extra
`notify_all` on the exit path, and none is needed: the last emit already
increments past `n` *and* broadcasts, so all three sleepers wake, fail the loop
condition and return on their own. Adding a defensive broadcast before `return`
is harmless but dead code — being able to say **which** notify releases the
other threads is the difference between having reasoned about it and having
copied it.
""",
        ),
    ],
}


class FizzBuzz:
    def __init__(self, n: int) -> None:
        self.n = n
        self._current = 1
        self._condition = threading.Condition()

    def _run(self, wants: Callable[[int], bool], emit: Callable[[int], None]) -> None:
        while True:
            with self._condition:
                while self._current <= self.n and not wants(self._current):
                    self._condition.wait()  # while, not if: a wake is only a hint
                if self._current > self.n:
                    return  # the last emit's broadcast already woke everyone
                emit(self._current)
                self._current += 1
                self._condition.notify_all()  # notify() here deadlocks 3 times in 4

    def fizz(self, print_fizz: Callable[[], None]) -> None:
        self._run(lambda i: i % 3 == 0 and i % 5 != 0, lambda _: print_fizz())

    def buzz(self, print_buzz: Callable[[], None]) -> None:
        self._run(lambda i: i % 5 == 0 and i % 3 != 0, lambda _: print_buzz())

    def fizzbuzz(self, print_fizzbuzz: Callable[[], None]) -> None:
        self._run(lambda i: i % 15 == 0, lambda _: print_fizzbuzz())

    def number(self, print_number: Callable[[int], None]) -> None:
        self._run(lambda i: i % 3 != 0 and i % 5 != 0, print_number)


def _run_once(n: int) -> list[str]:
    output: list[str] = []
    game = FizzBuzz(n)
    threads = [
        threading.Thread(target=game.number, args=(lambda i: output.append(str(i)),), daemon=True),
        threading.Thread(
            target=game.fizzbuzz, args=(lambda: output.append("fizzbuzz"),), daemon=True
        ),
        threading.Thread(target=game.buzz, args=(lambda: output.append("buzz"),), daemon=True),
        threading.Thread(target=game.fizz, args=(lambda: output.append("fizz"),), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive(), f"deadlock at n={n}"
    return output


def _expected(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("fizzbuzz")
        elif i % 3 == 0:
            out.append("fizz")
        elif i % 5 == 0:
            out.append("buzz")
        else:
            out.append(str(i))
    return out


def check() -> None:
    # n = 15 is the smallest n that exercises all four threads; n = 30 makes the
    # end-of-run notify_all bug show up twice as often.
    for n in (1, 3, 5, 14, 15, 30):
        target = _expected(n)
        for _ in range(10):
            assert _run_once(n) == target
    assert _expected(15)[-1] == "fizzbuzz"
    assert _expected(5) == ["1", "2", "fizz", "4", "buzz"]
