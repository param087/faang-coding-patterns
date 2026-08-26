"""Print Zero Even Odd — LeetCode 1116."""

from __future__ import annotations

import threading
from collections.abc import Callable

META = {
    "pattern": "concurrency",
    "symbol": "ZeroEvenOdd",
    "insight": "Zero runs every other slot, so let the zero thread decide which of the two number gates to open next.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Three threads share one instance. `zero` prints `0`, `even` prints the even
numbers, `odd` prints the odd ones. The output must be
`0102030405...` up to `n` — a zero before every number.

Ask whether the threads may be started in any order (they may), and confirm the
target: it is `010203`, **not** `012345` with zeroes sprinkled in. Every number
is preceded by exactly one zero.
""",
        ),
        (
            "The insight",
            """
Do not try to make `even` and `odd` coordinate with each other. They never talk.

`zero` runs in **every other slot**, so it is the natural arbiter: it holds the
counter, and after printing its `0` it releases either the odd gate or the even
gate depending on parity. Whichever number thread wakes prints and hands
control straight back to `zero`.

```
zero_gate = 1, odd_gate = 0, even_gate = 0

zero:  acquire(zero) -> print 0 -> release(odd if i is odd else even)
odd:   acquire(odd)  -> print i -> release(zero)
even:  acquire(even) -> print i -> release(zero)
```

One permit in flight, three gates, a single decision point. Turning a
three-way rendezvous into a hub-and-spoke is the move worth naming out loud.
""",
        ),
        (
            "Edge cases",
            """
- **`n = 0`** — every loop body runs zero times and all three threads return.
  A version that unconditionally acquires once before the loop hangs here.
- **`n = 1`** — output is `01`. The `even` thread's `range(2, n + 1, 2)` is
  empty, so it must exit without ever acquiring its gate. Writing the loops as
  `range(2, n + 1, 2)` and `range(1, n + 1, 2)` gets this for free; a
  `while True` with a break does not.
- **The last release is wasted.** After printing `n`, the number thread
  releases `zero_gate`, `zero` wakes, finds its loop exhausted and returns. A
  dangling permit is harmless — but if you switch to a `Condition`, that same
  final wake-up becomes the notify you must not forget, or the other threads
  block forever.
""",
        ),
    ],
}


class ZeroEvenOdd:
    def __init__(self, n: int) -> None:
        self.n = n
        self._zero_gate = threading.Semaphore(1)  # zero goes first
        self._even_gate = threading.Semaphore(0)
        self._odd_gate = threading.Semaphore(0)

    def zero(self, print_number: Callable[[int], None]) -> None:
        for i in range(1, self.n + 1):
            self._zero_gate.acquire()
            print_number(0)
            # The zero thread is the arbiter: it alone decides who goes next.
            if i % 2:
                self._odd_gate.release()
            else:
                self._even_gate.release()

    def even(self, print_number: Callable[[int], None]) -> None:
        for i in range(2, self.n + 1, 2):
            self._even_gate.acquire()
            print_number(i)
            self._zero_gate.release()

    def odd(self, print_number: Callable[[int], None]) -> None:
        for i in range(1, self.n + 1, 2):
            self._odd_gate.acquire()
            print_number(i)
            self._zero_gate.release()


def _run_once(n: int) -> str:
    """One trial, threads started in the least helpful order (even, odd, zero)."""
    output: list[str] = []
    printer = ZeroEvenOdd(n)

    def emit(value: int) -> None:
        output.append(str(value))

    threads = [
        threading.Thread(target=printer.even, args=(emit,), daemon=True),
        threading.Thread(target=printer.odd, args=(emit,), daemon=True),
        threading.Thread(target=printer.zero, args=(emit,), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
        assert not thread.is_alive(), f"deadlock at n={n}"
    return "".join(output)


def _expected(n: int) -> str:
    return "".join(f"0{i}" for i in range(1, n + 1))


def check() -> None:
    for n in (0, 1, 2, 3, 5, 12):
        target = _expected(n)
        for _ in range(15):
            assert _run_once(n) == target
    assert _expected(5) == "0102030405"
