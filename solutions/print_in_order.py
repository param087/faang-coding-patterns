"""Print in Order — LeetCode 1114."""

from __future__ import annotations

import threading
from collections.abc import Callable

META = {
    "pattern": "concurrency",
    "symbol": "Foo",
    "insight": "Two semaphores initialised to zero act as one-shot gates — each method releases the next and nothing spins.",
    "time": "O(1)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Three methods are called concurrently from three threads, in an arbitrary
order. Make them execute `first`, `second`, `third` regardless.

Ask: is each called exactly once; are they on separate threads (yes); may I
add state to the class (yes — that is the point).
""",
        ),
        (
            "The naive attempt, and why it is wrong",
            """
A shared boolean plus a spin loop "works" and is a bad answer:

- It **burns a CPU core** doing nothing.
- On a weak memory model it offers no guarantee the write is even visible to
  the other thread.

Naming that before giving the real solution is worth more than the solution
itself — it shows you have used threads rather than read about them.
""",
        ),
        (
            "The insight",
            """
Two semaphores, both initialised to **zero**, acting as one-shot gates:
`second` blocks until `first` releases it, and `third` blocks until `second`
does.

Nothing spins. A blocked thread is descheduled by the OS and costs nothing.
""",
        ),
        (
            "Why semaphores and not locks",
            """
A `Lock` is conceptually owned by whoever acquired it, and releasing another
thread's lock is at best confusing (and in some languages, undefined).

A **semaphore is explicitly a signal between threads**, which is exactly what
this is. Choosing the primitive that matches the intent is the judgement being
assessed.
""",
        ),
        (
            "Test it properly",
            """
Start the threads in the **wrong order** — third, second, first — and confirm
the output is still correct. If it is, the synchronisation is real rather than
accidental scheduling luck.

The test in this module does exactly that. Race conditions are probabilistic;
a single run that happens to pass proves nothing.
""",
        ),
        (
            "Follow-ups",
            """
- **Generalise to n methods** — an array of `n - 1` semaphores.
- **Print FooBar Alternately** — strict alternation needs **two gates facing
  each other**, because one shared lock lets a thread reacquire it and print
  twice.
- **Print Zero Even Odd** — three threads, a repeating pattern, and the same
  gate technique.
""",
        ),
    ],
}


class Foo:
    def __init__(self) -> None:
        # Zero-initialised: each gate stays shut until explicitly released.
        self._second_gate = threading.Semaphore(0)
        self._third_gate = threading.Semaphore(0)

    def first(self, print_first: Callable[[], None]) -> None:
        print_first()
        self._second_gate.release()

    def second(self, print_second: Callable[[], None]) -> None:
        self._second_gate.acquire()  # blocks, does not spin
        print_second()
        self._third_gate.release()

    def third(self, print_third: Callable[[], None]) -> None:
        self._third_gate.acquire()
        print_third()


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # Run it repeatedly: a single pass could be scheduling luck.
    for _ in range(20):
        output: list[str] = []
        foo = Foo()
        # Deliberately started in the wrong order.
        threads = [
            threading.Thread(target=foo.third, args=(lambda: output.append("third"),)),
            threading.Thread(target=foo.second, args=(lambda: output.append("second"),)),
            threading.Thread(target=foo.first, args=(lambda: output.append("first"),)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        assert output == ["first", "second", "third"], output
