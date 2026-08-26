"""Capacity To Ship Packages Within D Days — LeetCode 1011."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Packages must ship in order, so a capacity fixes the schedule — greedy filling is the only schedule, and it is monotone in capacity.",
    "time": "O(n log(sum − max))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Weights must be shipped **in the given order** within `days` days. Find the
smallest ship capacity that makes that possible.

The clarifying question that matters: **can the conveyor be reordered?** No —
and that single constraint is what makes the problem easy. If you could
reorder, this becomes bin packing, which is NP-hard, and the interviewer wants
to hear you notice the difference.
""",
        ),
        (
            "The insight",
            """
Once capacity is fixed, there is nothing left to decide. Loading greedily —
keep adding the next package until it would overflow, then start a new day —
is **optimal, not a heuristic**: deferring a package that fits can never
reduce the number of days when order is fixed.

So `days_needed(capacity)` is a well-defined function, and it is
**non-increasing**: a bigger ship never needs more days. Binary search the
smallest capacity with `days_needed(capacity) <= days`.

Bounds are where candidates lose the point:

- **low = max(weights)** — a single package heavier than the ship can never
  be loaded, so anything below this is not merely bad, it is infeasible.
- **high = sum(weights)** — one day, everything aboard.

Starting at `low = 1` still terminates, but it says you have not thought about
what makes a capacity valid at all.
""",
        ),
        (
            "Edge cases",
            """
- **`days >= len(weights)`** → the answer is exactly `max(weights)`, and the
  search must be able to return its low bound. Check that your loop can land
  on `low` without an extra iteration.
- **`days == 1`** → the answer is `sum(weights)`, i.e. the high bound. Both
  ends must be reachable.
- **One package.** low == high; the `while low < high` loop body never runs
  and returns immediately. A `low <= high` loop with `mid ± 1` bookkeeping is
  where off-by-ones breed — prefer the lower-bound form.
- **Counting days.** Start at `day = 1` with `load = 0`, not `day = 0`. The
  first package is already sailing on day one.
""",
        ),
    ],
}


def ship_within_days(weights: list[int], days: int) -> int:
    def days_needed(capacity: int) -> int:
        used, load = 1, 0
        for weight in weights:
            if load + weight > capacity:
                used += 1  # start a new day; order is fixed, so no choice here
                load = 0
            load += weight
        return used

    low, high = max(weights), sum(weights)
    while low < high:
        mid = (low + high) // 2
        if days_needed(mid) <= days:
            high = mid  # fits; try a smaller ship
        else:
            low = mid + 1

    return low


CASES = [
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5), 15),
    (([3, 2, 2, 4, 1, 4], 3), 6),
    (([1, 2, 3, 1, 1], 4), 3),
    (([1, 2, 3, 4, 5], 1), 15),
    (([1, 2, 3, 4, 5], 5), 5),
    (([10], 1), 10),
    (([5, 5, 5, 5], 2), 10),
]


def solve(weights: list[int], days: int) -> int:
    return ship_within_days(weights, days)
