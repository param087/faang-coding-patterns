"""Insert Delete GetRandom O(1) - Duplicates allowed — LeetCode 381."""

from __future__ import annotations

import random
from collections import Counter, defaultdict

META = {
    "pattern": "randomized",
    "symbol": "RandomizedCollection",
    "insight": "Same dense array and swap-with-last, but the index map holds a set per value, so removal must repair a position inside a set.",
    "time": "O(1) average for insert, remove and getRandom",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A **multiset** with `insert`, `remove` and `getRandom`, all O(1) average.
`insert` reports whether the value was absent beforehand; `remove` deletes one
occurrence and reports whether anything was there; `getRandom` is uniform over
**occurrences**, so a value present three times is three times as likely.

That last clause is the one to confirm out loud. Uniform-over-values and
uniform-over-occurrences are different structures, and the wrong reading gives
you a much easier and completely wrong answer.

Ask, too, whether `remove` may delete *any* occurrence or a specified one.
Any — which is what buys you the O(1).
""",
        ),
        (
            "The insight",
            """
Start from [Insert Delete GetRandom O(1)](../insert-delete-getrandom-o1/) and
change exactly one thing.

- `values`: a dense list, so `randrange(len(values))` is a uniform draw over
  occurrences for free.
- `positions`: `value → set of indices` instead of `value → index`, because a
  value now lives in several slots.

Removal is still **swap the doomed slot with the last one and pop**, which
avoids the O(n) shift and keeps the array dense. The only new work is that the
moved element's index has to be repaired *inside its set* rather than
overwritten.

Set membership, add and discard are all O(1) average, so nothing regresses.
Pop an arbitrary index from the target's set — `set.pop()` is fine, since any
occurrence may go.
""",
        ),
        (
            "The remove, in the only order that works",
            """
Four lines, and three of the four aliasing cases will bite you if you write
them in a different order:

```python
out  = self.positions[val].pop()          # some slot holding val
last = self.values[-1]
self.values[out] = last
self.positions[last].add(out)             # the moved element gains its new slot
self.positions[last].discard(len(self.values) - 1)   # and loses the old one
self.values.pop()
```

Add **before** discard, and use `discard` rather than `remove`. Then the two
nasty cases fall out for free:

- **The doomed slot is the last slot.** `add(out)` puts back the index that
  was just popped, then `discard` takes it away again. Net effect correct.
- **`val` equals the last value** (a duplicate at the tail). The same set is
  being edited twice; add-then-discard leaves it holding `out` and not the
  stale tail index, which is exactly right since `values[out]` is still `val`.

Discard-then-add gets both of these wrong and leaves a stale index that
corrupts the array on some *later* remove — one operation late, which is the
worst kind of bug to find in an interview.

Also guard the empty-set case: a `defaultdict` will happily create an empty
set for a value that was never inserted, so test truthiness before popping or
`set.pop()` raises `KeyError`.
""",
        ),
    ],
}


class RandomizedCollection:
    def __init__(self) -> None:
        self.values: list[int] = []
        self.positions: defaultdict[int, set[int]] = defaultdict(set)

    def insert(self, val: int) -> bool:
        already_present = bool(self.positions[val])
        self.positions[val].add(len(self.values))
        self.values.append(val)
        return not already_present

    def remove(self, val: int) -> bool:
        slots = self.positions[val]
        if not slots:  # defaultdict may have just created this empty set
            return False

        out = slots.pop()  # any occurrence will do
        last = self.values[-1]
        self.values[out] = last
        self.positions[last].add(out)  # add before discard: they may be the same set
        self.positions[last].discard(len(self.values) - 1)
        self.values.pop()
        return True

    def get_random(self) -> int:
        return self.values[random.randrange(len(self.values))]


CASES: list[tuple[tuple, object]] = []


def _invariant(collection: RandomizedCollection) -> None:
    """Every recorded position must actually hold its value, and vice versa."""
    for value, slots in collection.positions.items():
        for slot in slots:
            assert collection.values[slot] == value, f"stale index {slot} for {value}"
    total = sum(len(slots) for slots in collection.positions.values())
    assert total == len(collection.values)


def check() -> None:
    c = RandomizedCollection()
    assert c.insert(1) is True  # first occurrence
    assert c.insert(1) is False  # already present
    assert c.insert(2) is True
    assert c.remove(1) is True
    assert sorted(c.values) == [1, 2]
    assert c.remove(3) is False  # never inserted
    _invariant(c)

    # Removing the tail occurrence of a value that is also the tail element.
    tail = RandomizedCollection()
    for value in (5, 5, 5):
        tail.insert(value)
    assert tail.remove(5) is True
    assert tail.values == [5, 5]
    _invariant(tail)
    assert tail.remove(5) is True
    assert tail.remove(5) is True
    assert tail.remove(5) is False
    assert tail.values == []

    # The moved element is a duplicate of the removed one — the aliasing case.
    alias = RandomizedCollection()
    for value in (4, 9, 4):
        alias.insert(value)
    assert alias.remove(4) is True
    _invariant(alias)
    assert sorted(alias.values) == [4, 9]
    assert alias.remove(4) is True
    assert alias.values == [9]
    _invariant(alias)

    # A long interleaved run: the invariant catches any stale index left behind.
    stress = RandomizedCollection()
    rng = random.Random(20250825)
    live: list[int] = []
    for step in range(1_500):
        if live and rng.random() < 0.45:
            victim = live.pop(rng.randrange(len(live)))
            assert stress.remove(victim) is True
        else:
            value = rng.randrange(12)  # few distinct values, so many duplicates
            stress.insert(value)
            live.append(value)
        if step % 20 == 0:
            _invariant(stress)
    _invariant(stress)
    assert sorted(stress.values) == sorted(live)

    # getRandom is uniform over OCCURRENCES, not values: 2 is twice as likely.
    weighted = RandomizedCollection()
    for value in (1, 2, 2):
        weighted.insert(value)
    draws = 30_000
    spread = Counter(weighted.get_random() for _ in range(draws))
    assert set(spread) == {1, 2}
    assert abs(spread[2] - draws * 2 / 3) < 500
