"""Implement Queue using Stacks — LeetCode 232."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "symbol": "MyQueue",
    "insight": "Pouring one stack into another reverses it, so a second stack turns LIFO into FIFO — provided you only pour when it is empty.",
    "time": "O(1) amortised per operation; O(n) worst case for a single pop",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Build a FIFO queue — `push`, `pop`, `peek`, `empty` — using only stack
operations: push to the top, pop from the top, peek at the top, size, empty.

The clarifying question that shapes the answer: **is amortised O(1) acceptable,
or do you need worst-case O(1)?** Amortised is what LeetCode asks for and what
two stacks give you. Worst-case O(1) per operation is a genuinely harder
problem (it needs incremental copying), and knowing the difference is most of
what is being tested. Ask it before you write anything.

Also worth confirming: `pop` and `peek` are only called on a non-empty queue,
which is why there is no guard below.
""",
        ),
        (
            "The insight",
            """
A stack reverses whatever you pour into it. Pop everything out of stack `in`
and push it into stack `out`, and the oldest element — the one the queue wants
— is now on top of `out`.

So: `push` always goes to `in`; `pop` and `peek` always come from `out`, and
`out` is refilled from `in` **only when it is empty**.

That last clause is the entire algorithm. Refilling eagerly on every push, or
whenever `in` is non-empty, is O(n) per operation *and* wrong: an element
pushed after a partial drain would land on top of `out`, ahead of older
elements, and come out first. The `if not self._out` guard is what preserves
FIFO, not just what makes it fast.
""",
        ),
        (
            "Why it is amortised O(1)",
            """
The `while` loop makes a single `pop` look O(n), and it is — once. But each
element is moved from `in` to `out` **exactly once in its lifetime**, so across
n pushes and n pops the total work is at most 2n stack operations. Divided over
2n operations, that is O(1) each.

Say "amortised", and say the accounting: every element is pushed twice and
popped twice, full stop. This is the part interviewers actually score, and it
is the same argument as the monotonic-stack one — a nested loop is not
automatically quadratic when the inner loop consumes a budget the outer loop
pays for.

The worst case for a *single* call is still O(n), which matters if the queue is
behind a latency SLA rather than a throughput one. That is the opening for the
worst-case-O(1) follow-up: keep a third stack and move one element per
operation instead of all of them.
""",
        ),
    ],
}


class MyQueue:
    """FIFO on top of two LIFOs. `_in` takes arrivals, `_out` serves departures."""

    def __init__(self) -> None:
        self._in: list[int] = []
        self._out: list[int] = []

    def push(self, x: int) -> None:
        self._in.append(x)

    def _transfer(self) -> None:
        # Only when `_out` is empty: a partial drain would put newer elements
        # on top of older ones and break FIFO.
        if not self._out:
            while self._in:
                self._out.append(self._in.pop())

    def pop(self) -> int:
        self._transfer()
        return self._out.pop()

    def peek(self) -> int:
        self._transfer()
        return self._out[-1]

    def empty(self) -> bool:
        return not self._in and not self._out


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    queue = MyQueue()
    assert queue.empty() is True

    queue.push(1)
    queue.push(2)
    assert queue.peek() == 1
    assert queue.pop() == 1
    assert queue.empty() is False

    # A push that arrives while `_out` still holds an older element. An eager
    # or unconditional transfer returns 3 here.
    queue.push(3)
    assert queue.peek() == 2
    assert queue.pop() == 2
    assert queue.pop() == 3
    assert queue.empty() is True

    # Refill after a full drain, then interleave again.
    for value in range(5):
        queue.push(value)
    assert [queue.pop() for _ in range(3)] == [0, 1, 2]
    queue.push(99)
    assert [queue.pop() for _ in range(3)] == [3, 4, 99]
    assert queue.empty() is True

    single = MyQueue()
    single.push(7)
    assert single.peek() == 7
    assert single.pop() == 7
    assert single.empty() is True
