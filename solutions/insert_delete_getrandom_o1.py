"""Insert Delete GetRandom O(1) — LeetCode 380."""

from __future__ import annotations

import random

META = {
    "pattern": "randomized",
    "symbol": "RandomizedSet",
    "insight": "Swap the doomed element with the last one and pop — no shifting, so removal is O(1) and the array stays dense.",
    "time": "O(1) for all three operations",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A set supporting `insert`, `remove` and `getRandom` — all **O(1) average**,
with `getRandom` uniform over the current elements.

Ask: are duplicates allowed (the follow-up variant allows them and changes the
structure); must `getRandom` be uniform over *values* or *occurrences*; do
`insert`/`remove` return whether they changed anything (yes).
""",
        ),
        (
            "The tension",
            """
State it first — it is what motivates the answer:

- A **hash set** gives O(1) membership but cannot pick uniformly at random,
  because there is no way to index into it.
- A **list** gives O(1) random access but O(n) removal from the middle, because
  everything after the hole must shift.

Neither alone meets the contract. So keep both, and find a way to remove
without shifting.
""",
        ),
        (
            "The trick",
            """
To remove an element: **swap it with the last one, then pop.**

No shifting, so removal is O(1). The array stays dense, so `random.randrange`
over its length remains uniform.

That is the entire insight, and it recurs — it is how you delete from any
array-backed structure where order does not matter.
""",
        ),
        (
            "The detail that breaks it",
            """
After the swap you must update the map entry for the element that **moved**,
not just delete the one that left.

Forgetting leaves a stale index, and the *next* removal reads it and corrupts
the array. The failure is one operation late, which makes it hard to debug if
you have not anticipated it.

**Dry-run** insert 1, insert 2, remove 1: the 2 moves into slot 0 and its map
entry must follow it. That is the whole bug surface.
""",
        ),
        (
            "The order of operations",
            """
Write the last-element swap *before* the pop, and delete the departing key
*after* reassigning the moved one — otherwise removing the last element
deletes the entry you just wrote.
""",
        ),
        (
            "Follow-ups",
            """
- **Duplicates allowed** (LeetCode 381). The map becomes `value → set of
  indices`, and removal picks an arbitrary one. Still O(1), and noticeably
  fiddlier — the swap must update the moved element's index *within its set*.
- **Weighted random** — see Random Pick with Weight, which is prefix sums plus
  binary search.
""",
        ),
    ],
}


class RandomizedSet:
    def __init__(self) -> None:
        self.values: list[int] = []
        self.index: dict[int, int] = {}  # value -> its position in `values`

    def insert(self, value: int) -> bool:
        if value in self.index:
            return False
        self.index[value] = len(self.values)
        self.values.append(value)
        return True

    def remove(self, value: int) -> bool:
        position = self.index.get(value)
        if position is None:
            return False

        # Swap with the last element so the pop is O(1) and the array stays dense.
        last = self.values[-1]
        self.values[position] = last
        self.index[last] = position  # the MOVED element's index must follow it
        self.values.pop()
        del self.index[value]  # after, so removing the last element is safe
        return True

    def get_random(self) -> int:
        return self.values[random.randrange(len(self.values))]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    s = RandomizedSet()
    assert s.insert(1) is True
    assert s.insert(1) is False  # already present
    assert s.remove(2) is False  # not present
    assert s.insert(2) is True
    assert s.remove(1) is True
    assert s.get_random() == 2  # only one element left
    assert s.insert(1) is True
    assert sorted(s.values) == [1, 2]

    # Removing the last element must not corrupt the map.
    tail = RandomizedSet()
    tail.insert(1)
    tail.insert(2)
    assert tail.remove(2) is True
    assert tail.values == [1]
    assert tail.index == {1: 0}

    # The moved-element case, run to exhaustion.
    many = RandomizedSet()
    for v in range(10):
        many.insert(v)
    for v in range(0, 10, 2):
        assert many.remove(v) is True
    assert sorted(many.values) == [1, 3, 5, 7, 9]
    # Every surviving value must still map to its true position.
    for value, position in many.index.items():
        assert many.values[position] == value

    # getRandom must eventually produce every element.
    seen = {many.get_random() for _ in range(500)}
    assert seen == {1, 3, 5, 7, 9}
