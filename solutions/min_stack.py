"""Min Stack — LeetCode 155."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "symbol": "MinStack",
    "insight": "Store the running minimum alongside every value, so popping restores the previous minimum for free.",
    "time": "O(1) for every operation",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A stack supporting `push`, `pop`, `top` and `getMin`, **all in O(1)**.

Ask: will `getMin` be called on an empty stack; do `pop` and `top` return
anything; are duplicate minima possible (yes, and the compressed variant has
to handle them).
""",
        ),
        (
            "The naive attempt — name it, then kill it",
            """
> "I could keep a single `min` field — but when I pop the minimum, I have no
> way to find the next one without scanning, so that breaks the O(1)
> requirement."

Naming the broken idea and saying *why* it breaks is worth more than jumping
straight to the answer. It shows you understand the constraint rather than
having memorised the trick.
""",
        ),
        (
            "The insight",
            """
Store `(value, minimum at or below this point)` pairs.

Every entry remembers what the minimum was when it was pushed, so popping
**restores the previous minimum automatically** — no scan, no recomputation.

The general move: when a structure needs an extra O(1) query, consider storing
the answer to that query at every level rather than recomputing it.
""",
        ),
        (
            "The follow-up",
            """
"Can you reduce the space?"

A second stack that pushes **only when a new minimum arrives**. Smaller in
practice, same O(n) worst case.

The detail that matters: use `<=`, not `<`, when deciding whether to push. With
`<`, a duplicate minimum is not recorded, and popping the first copy removes
the minimum while an equal value is still in the stack. That is the bug in the
compressed version, and mentioning it unprompted is a strong signal.
""",
        ),
        (
            "Follow-ups",
            """
- **Max Stack** — the same idea, plus `popMax`, which needs a heap or an
  ordered structure because you must remove from the middle.
- **Min Queue** — a queue does not have this property for free; it needs two
  stacks or a [monotonic deque](../../patterns/monotonic-stack/).
""",
        ),
    ],
}


class MinStack:
    def __init__(self) -> None:
        # Each entry remembers the minimum as of when it was pushed.
        self._stack: list[tuple[int, int]] = []

    def push(self, value: int) -> None:
        smallest = value if not self._stack else min(value, self._stack[-1][1])
        self._stack.append((value, smallest))

    def pop(self) -> int:
        return self._stack.pop()[0]  # the previous minimum returns for free

    def top(self) -> int:
        return self._stack[-1][0]

    def get_min(self) -> int:
        return self._stack[-1][1]


class MinStackCompact:
    """The space-reduced variant: a second stack, pushed only on a new minimum."""

    def __init__(self) -> None:
        self._stack: list[int] = []
        self._minima: list[int] = []

    def push(self, value: int) -> None:
        self._stack.append(value)
        # `<=`, not `<`: a duplicate minimum must be recorded too.
        if not self._minima or value <= self._minima[-1]:
            self._minima.append(value)

    def pop(self) -> int:
        value = self._stack.pop()
        if value == self._minima[-1]:
            self._minima.pop()
        return value

    def top(self) -> int:
        return self._stack[-1]

    def get_min(self) -> int:
        return self._minima[-1]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    for cls in (MinStack, MinStackCompact):
        stack = cls()
        for value in (-2, 0, -3):
            stack.push(value)
        assert stack.get_min() == -3
        assert stack.pop() == -3
        assert stack.top() == 0
        assert stack.get_min() == -2

        # Duplicate minima: the `<=` case that breaks a naive compact version.
        dup = cls()
        for value in (1, 1, 2):
            dup.push(value)
        assert dup.get_min() == 1
        dup.pop()  # removes 2
        assert dup.get_min() == 1
        dup.pop()  # removes one of the 1s
        assert dup.get_min() == 1  # the other 1 is still there
        dup.pop()

        single = cls()
        single.push(5)
        assert single.get_min() == 5
        assert single.top() == 5
