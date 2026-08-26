"""Magnetic Force Between Two Balls — LeetCode 1552."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Maximising the minimum gap: guess the gap, place balls greedily as early as possible, and count how many fit.",
    "time": "O(n log n) to sort, then O(n log(max position))",
    "space": "O(n) for the sorted copy",
    "sections": [
        (
            "What it asks",
            """
Put `m` balls into baskets at the given positions so that the **smallest**
distance between any two balls is as large as possible. Return that distance.

The phrase "minimum magnetic force between any two balls" is just "the
smallest gap between consecutive chosen positions" — once the positions are
sorted, only adjacent pairs matter, since any non-adjacent pair is at least as
far apart. Say that out loud; it is the observation that makes the check O(n).
""",
        ),
        (
            "The insight",
            """
This is the mirror image of the minimise-the-maximum problems: here you
**maximise the minimum**, so the predicate flips.

`can_place(gap)` — can I fit `m` balls with every consecutive pair at least
`gap` apart? Sort, put the first ball in the leftmost basket, then walk right
taking every basket that is at least `gap` beyond the last one taken. Greedy
placement leftmost-first is optimal: leaving a ball further right can only
reduce the room available for the ones after it.

Feasibility is monotone **downward** — if `gap` works, every smaller gap works.
So the feasible gaps form a *prefix* and you binary search for the largest one,
which means the loop shape changes: bias `mid` upward with
`mid = (low + high + 1) // 2` and move `low = mid` on success.

Get that `+ 1` wrong and `low = mid` with `low = high − 1` spins forever. It is
the single most common way this problem is failed in an interview.
""",
        ),
        (
            "Bounds and edges",
            """
- **low = 1.** Positions are distinct, so a gap of 1 always works when
  `m <= n`.
- **high = (max − min) // (m − 1).** The `m` balls span at most `max − min`
  and there are `m − 1` gaps, so no gap can exceed the average. Using
  `max − min` instead still works but wastes a couple of iterations and misses
  a chance to show you have bounded the answer properly.
- **`m == 2`** → the answer is always `max − min`: put one ball at each end.
  Check your high bound reduces to exactly that.
- **`m == n`** → every basket is used, and the answer is the minimum adjacent
  gap in the sorted array. A useful hand-check for the greedy.
- **Sorting.** The input is unsorted. `sorted(position)` rather than
  `position.sort()` keeps the function pure, which matters when the same input
  is reused across calls.
""",
        ),
    ],
}


def max_distance(position: list[int], m: int) -> int:
    baskets = sorted(position)  # copy, not in-place: keep the caller's list intact

    def can_place(gap: int) -> bool:
        placed, last = 1, baskets[0]
        for basket in baskets[1:]:
            if basket - last >= gap:
                placed += 1
                last = basket
                if placed >= m:
                    return True
        return placed >= m

    low, high = 1, (baskets[-1] - baskets[0]) // (m - 1)
    while low < high:
        mid = (low + high + 1) // 2  # bias up: we move low onto mid
        if can_place(mid):
            low = mid  # this gap fits; try a wider one
        else:
            high = mid - 1

    return low


CASES = [
    (([1, 2, 3, 4, 7], 3), 3),
    (([5, 4, 3, 2, 1, 1000000000], 2), 999999999),
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4), 3),
    (([79, 74, 57, 22], 4), 5),
    (([1, 2, 3, 4, 7], 5), 1),
    (([1, 2], 2), 1),
]


def solve(position: list[int], m: int) -> int:
    return max_distance(position, m)
