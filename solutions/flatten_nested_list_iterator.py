"""Flatten Nested List Iterator — LeetCode 341."""

from __future__ import annotations

META = {
    "pattern": "stack",
    "symbol": "NestedIterator",
    "insight": "Hold a stack of partially-consumed lists instead of a flattened array, and hasNext does the descending so next stays trivial.",
    "time": "O(1) amortised per next/hasNext; O(1) to construct",
    "space": "O(d) for nesting depth d, not O(total elements)",
    "sections": [
        (
            "What it asks",
            """
Given a list whose elements are either integers or further such lists,
implement an iterator with `next()` and `hasNext()` that yields the integers in
order.

The nested elements arrive as an opaque interface — `isInteger()`,
`getInteger()`, `getList()` — not as raw Python lists. That matters: you cannot
`isinstance`-check your way out, and the interface is deliberately the only
thing you may call. (The class below reconstructs that interface from plain
nested lists so the module is runnable and testable on its own.)

The question to ask: **is the input finite and already in memory, or could it
be huge or streamed?** The answer decides between the two solutions below, and
asking it is the difference between passing the problem and passing the
interview.
""",
        ),
        (
            "The insight",
            """
The accepted-but-uninteresting answer flattens everything in the constructor
into one list, then serves it with an index. LeetCode accepts it. It also
allocates O(total elements) up front and does all the work before the caller
asks for a single value — which defeats the purpose of an iterator, and an
interviewer who chose this problem chose it for the lazy version.

Lazily, the state you need is exactly "where am I, in each list I have
descended into": a **stack of partially-consumed lists**. Push the input list;
to advance, look at the top:

- top is exhausted → pop it, you have finished that nesting level;
- top's next element is an integer → stop, that is the answer;
- top's next element is a list → remove it from the top and push its contents.

Each list is pushed once and popped once, so across the whole traversal the
work is linear and each call is O(1) amortised. Space is the **nesting depth**,
not the element count — the win that the eager version throws away.

Store each level reversed so "next element" is `list[-1]` and consuming it is
`pop()`, which is O(1); popping from the front of a Python list is not.
""",
        ),
        (
            "hasNext does the work, not next",
            """
The temptation is to make `next()` advance the stack and `hasNext()` a cheap
truthiness check. That breaks on empty lists: for `[[], [], [1]]` the stack is
non-empty while no integer remains reachable, so `hasNext()` returns `True` and
`next()` blows up. `[[[[]]]]` is the same trap, three levels deep.

You cannot answer "is there a next?" without descending far enough to find one
— so `hasNext()` must be the method that drives the loop, leaving `next()` as a
single `pop()`. Two consequences to state:

- **`hasNext()` must be idempotent.** It advances past *containers* but never
  consumes an integer; it stops with the integer still on the stack. Calling it
  twice must not skip a value, and the harness below asserts exactly that.
- **`next()` should be safe on its own.** LeetCode promises `hasNext()` is
  called first; real callers do not. Calling `hasNext()` from inside `next()`
  costs nothing and removes a class of caller bugs.

Follow-up worth having ready: turning this into a real Python iterator is
`__iter__`/`__next__` with `StopIteration`, or — much shorter — a recursive
generator with `yield from`. The generator is lazy too and is what you would
actually ship; the stack version is what you write when the interviewer says
"without recursion".
""",
        ),
    ],
}


class NestedInteger:
    """The opaque interface LeetCode supplies, rebuilt from plain Python values."""

    def __init__(self, value: int | list) -> None:
        if isinstance(value, list):
            self._integer: int | None = None
            self._list = [NestedInteger(item) for item in value]
        else:
            self._integer = value
            self._list = []

    def is_integer(self) -> bool:
        return self._integer is not None

    def get_integer(self) -> int:
        if self._integer is None:
            raise ValueError("not an integer")
        return self._integer

    def get_list(self) -> list[NestedInteger]:
        return self._list


class NestedIterator:
    """A stack of partially-consumed levels, each stored reversed so pop() is O(1)."""

    def __init__(self, nested_list: list[NestedInteger]) -> None:
        self._stack: list[list[NestedInteger]] = [list(reversed(nested_list))]

    def has_next(self) -> bool:
        while self._stack:
            top = self._stack[-1]
            if not top:
                self._stack.pop()  # this level is finished
            elif top[-1].is_integer():
                return True  # stop *without* consuming it — idempotent
            else:
                self._stack.append(list(reversed(top.pop().get_list())))
        return False

    def next(self) -> int:
        if not self.has_next():
            raise StopIteration
        return self._stack[-1].pop().get_integer()


def flatten(nested: list) -> list[int]:
    iterator = NestedIterator([NestedInteger(item) for item in nested])
    out: list[int] = []
    while iterator.has_next():
        out.append(iterator.next())
    return out


CASES = [
    (([[1, 1], 2, [1, 1]],), [1, 1, 2, 1, 1]),
    (([1, [4, [6]]],), [1, 4, 6]),
    (([[], [1], [], [2, []], 3],), [1, 2, 3]),  # empty lists between values
    (([[[[]]]],), []),  # nesting with no integers at all
    (([[]],), []),
    (([[-1, [-2]], 0],), [-1, -2, 0]),  # negatives, and 0 is not "empty"
    (([],), []),
]


def solve(nested: list) -> list[int]:
    return flatten(nested)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    iterator = NestedIterator([NestedInteger(item) for item in [[], [1], [], [2, [3]]]])
    assert iterator.has_next() is True
    assert iterator.has_next() is True  # idempotent: no value consumed
    assert iterator.next() == 1
    assert [iterator.next() for _ in range(2)] == [2, 3]
    assert iterator.has_next() is False

    # next() must be safe without a preceding has_next().
    empty = NestedIterator([NestedInteger(item) for item in [[[]], []]])
    assert empty.has_next() is False
    try:
        empty.next()
    except StopIteration:
        pass
    else:  # pragma: no cover
        raise AssertionError("next() on an exhausted iterator must raise")
