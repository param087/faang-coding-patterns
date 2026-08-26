"""Implement Stack using Queues — LeetCode 225."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "stack",
    "symbol": "MyStack",
    "insight": "Rotate the queue onto itself after every push so the newest element sits at the front — pay the O(n) at a time you choose.",
    "time": "O(n) for push, O(1) for pop, top and empty",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Build a LIFO stack — `push`, `pop`, `top`, `empty` — using only queue
operations: enqueue at the back, dequeue from the front, peek at the front,
size, empty.

The mirror of LeetCode 232, and the interesting difference is that **here you
cannot get amortised O(1) on everything**. A queue does not reverse what you
pour into it the way a stack does, so one of the two ends has to pay O(n) on
every call. The question is really "which operation do you choose to make
expensive, and can you justify it?"

Confirm that `pop` and `top` are only called on a non-empty stack — that is why
there is no guard below.
""",
        ),
        (
            "The insight",
            """
Since somebody has to pay, pay at **push**, where the cost is a single known
rotation rather than a surprise.

Enqueue the new element at the back, then dequeue-and-re-enqueue the other
`n - 1` elements. Everything that was in front of it moves behind it, so the
newest element is now at the front — exactly where `pop` and `top` want it.
Both of those become one-liners.

Concretely, pushing `3` onto `[2, 1]` (front first) gives `[2, 1, 3]`, then two
rotations give `[1, 3, 2]` → `[3, 2, 1]`. Front is newest, and the invariant
"the queue is the stack, top-first" holds after every operation.

One honest note: `deque.rotate` would do this in one call, but it is not a
queue operation, and using it dodges the entire point of the exercise. Write
the `append(popleft())` loop.
""",
        ),
        (
            "One queue or two, and which to say",
            """
The two-queue version is the one most people have memorised: push into the
empty queue, drain the other one behind it, swap the references. It is the same
O(n) push with an extra allocation and an extra variable — strictly worse, and
saying so is a small, cheap signal.

The variant genuinely worth mentioning is the **costly-pop** one: push is O(1)
straight onto the back, and `pop` drains `n - 1` elements into the second queue
to reach the last one. Same asymptotics, opposite profile.

Which to pick is a workload question, and that is the answer to give:

- pushes dominate (a write-heavy log) → make `pop` expensive;
- reads dominate, or `top` is hot → make `push` expensive, as below;
- neither dominates → prefer the version with fewer moving parts, which is the
  single queue.

Getting asked "can you do better than O(n)?" is the trap. With only queue
primitives you cannot: a queue can only expose its front, and the front is the
*oldest* element, so reaching the newest costs a full traversal. Say that
plainly rather than hunting for a trick.
""",
        ),
    ],
}


class MyStack:
    """LIFO on one FIFO. Invariant: the front of the queue is the stack top."""

    def __init__(self) -> None:
        self._queue: deque[int] = deque()

    def push(self, x: int) -> None:
        self._queue.append(x)
        # Rotate everything that was ahead of `x` around behind it.
        for _ in range(len(self._queue) - 1):
            self._queue.append(self._queue.popleft())

    def pop(self) -> int:
        return self._queue.popleft()

    def top(self) -> int:
        return self._queue[0]

    def empty(self) -> bool:
        return not self._queue


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    stack = MyStack()
    assert stack.empty() is True

    stack.push(1)
    assert stack.top() == 1  # single element: the rotation loop must run zero times
    stack.push(2)
    assert stack.top() == 2
    assert stack.pop() == 2
    assert stack.top() == 1
    assert stack.empty() is False
    assert stack.pop() == 1
    assert stack.empty() is True

    # Interleave pushes and pops so the invariant is re-established mid-sequence.
    for value in (1, 2, 3):
        stack.push(value)
    assert stack.pop() == 3
    stack.push(4)
    assert stack.top() == 4
    assert [stack.pop() for _ in range(3)] == [4, 2, 1]
    assert stack.empty() is True

    # Refill after a full drain — LIFO order across the whole run.
    deep = MyStack()
    for value in range(6):
        deep.push(value)
    assert [deep.pop() for _ in range(6)] == [5, 4, 3, 2, 1, 0]
    assert deep.empty() is True
