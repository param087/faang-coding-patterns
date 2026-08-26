"""Random Flip Matrix — LeetCode 519."""

from __future__ import annotations

import random
from collections import Counter

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Run Fisher-Yates over the flattened index space, recording only the swaps you actually made, so memory is O(flips) not O(rows x cols).",
    "time": "O(1) per flip and per reset amortised",
    "space": "O(number of flips since the last reset)",
    "sections": [
        (
            "What it asks",
            """
An `m × n` grid of zeros. `flip()` picks a uniformly random **still-zero**
cell, sets it to one and returns its coordinates; `reset()` clears everything.

The constraints are the problem: `m · n` can be 10⁶ while the number of calls
is at most 1,000. So the grid must never be materialised, and `flip()` must
not scan. Both the O(mn) memory and the "keep retrying until you hit a zero"
loop are ruled out by numbers, not by taste — ask for those bounds if they are
not given, because they are what select the answer.

Retrying is worth pricing anyway: once 90% of a small grid is flipped, the
expected number of retries per call is 10, and the worst case is unbounded.
""",
        ),
        (
            "The insight",
            """
Flatten the grid to indices `0 … mn−1`; cell `i` is `(i // n, i % n)`. Now the
task is "draw distinct indices uniformly at random", which is exactly a
**Fisher-Yates shuffle consumed one element at a time**.

The shuffle keeps an unused prefix `[0, remaining)`. Each call draws
`k = randrange(remaining)`, yields whatever value sits in slot k, then moves
the value from the last live slot into slot k and shrinks `remaining`.

The only obstacle is that you cannot afford the backing array of 10⁶ entries.
You do not need it: slot i holds value i **unless it was written**, so keep a
hash map of only the slots that were touched. `moved.get(k, k)` reads the
array lazily. After 1,000 flips the map holds at most 1,000 entries instead of
10⁶ — a **virtual array**, and the same trick works for any sparse permutation.
""",
        ),
        (
            "The line everyone gets wrong",
            """
When you move the tail into the hole, you must move the tail's **current
value**, not its index:

```python
tail = self.moved.pop(self.remaining, self.remaining)   # right
tail = self.remaining                                   # wrong
```

The wrong version is correct until a slot near the end has itself already been
overwritten by an earlier flip — then it re-injects an index that has already
been handed out, and `flip()` returns a duplicate cell. On a 2×2 grid it takes
two specific draws to trigger, so it survives casual testing and fails the
uniformity assertion below (24 orderings of a 1×4 grid, each within 6% of even).

Two more details:

- `pop` rather than `get` on the tail, and skip the write when `k` is the last
  slot. That keeps the map at O(flips) instead of growing forever, which is
  the whole point of using a map.
- `reset()` clears the map and restores `remaining`. Flipping past the end
  should raise rather than loop — `randrange(0)` does that for free, and it is
  worth saying that you would validate rather than hang.
""",
        ),
    ],
}


class Solution:
    def __init__(self, m: int, n: int) -> None:
        self.m = m
        self.n = n
        self.remaining = m * n
        self.moved: dict[int, int] = {}  # slot -> value, only where they differ

    def reset(self) -> None:
        self.remaining = self.m * self.n
        self.moved.clear()

    def flip(self) -> list[int]:
        k = random.randrange(self.remaining)  # raises once the grid is full
        index = self.moved.get(k, k)  # the virtual array reads as identity

        self.remaining -= 1
        tail = self.moved.pop(self.remaining, self.remaining)  # its VALUE, not its index
        if k != self.remaining:
            self.moved[k] = tail

        return [index // self.n, index % self.n]


CASES: list[tuple[tuple, object]] = []


def _drain(solution: Solution) -> list[tuple[int, int]]:
    solution.reset()
    return [tuple(solution.flip()) for _ in range(solution.m * solution.n)]


def check() -> None:
    # A 1x1 grid: one flip, then exhaustion, then reset makes it available again.
    single = Solution(1, 1)
    assert single.flip() == [0, 0]
    raised = False
    try:
        single.flip()
    except ValueError:  # randrange(0)
        raised = True
    assert raised, "flipping a full grid must fail loudly, not loop"
    single.reset()
    assert single.flip() == [0, 0]

    # Draining any grid yields every cell exactly once. This is what the
    # tail-index bug breaks — it returns duplicates.
    for rows, cols in ((2, 2), (1, 5), (5, 1), (3, 4)):
        grid = Solution(rows, cols)
        for _ in range(200):
            cells = _drain(grid)
            assert len(set(cells)) == rows * cols
            assert set(cells) == {(r, c) for r in range(rows) for c in range(cols)}

    # The first flip must be uniform over all 9 cells of a 3x3.
    picker = Solution(3, 3)
    draws = 30_000
    first = Counter()
    for _ in range(draws):
        picker.reset()
        first[tuple(picker.flip())] += 1
    assert len(first) == 9
    assert all(abs(count - draws / 9) < 300 for count in first.values())

    # Stronger: the whole ORDER must be uniform, all 24 permutations of a 1x4
    # grid within 6% of even. Position-level uniformity alone would not catch
    # a broken swap.
    line = Solution(1, 4)
    trials = 12_000
    orders = Counter(tuple(cell[1] for cell in _drain(line)) for _ in range(trials))
    assert len(orders) == 24, f"saw {len(orders)} of 24 orderings"
    for order, count in orders.items():
        assert abs(count - trials / 24) < 140, f"{order} came up {count} times"

    # Memory is O(flips), not O(m*n): a million-cell grid after 5 flips.
    huge = Solution(1_000, 1_000)
    seen = {tuple(huge.flip()) for _ in range(5)}
    assert len(seen) == 5
    assert len(huge.moved) <= 5
    assert huge.remaining == 1_000_000 - 5
    huge.reset()
    assert huge.moved == {}

    # Row-major decoding: index i must land at (i // n, i % n).
    wide = Solution(2, 7)
    assert all(0 <= r < 2 and 0 <= c < 7 for r, c in _drain(wide))
