"""Koko Eating Bananas — LeetCode 875."""

from __future__ import annotations

import math

META = {
    "pattern": "binary-search-answer",
    "insight": "You are not searching the array — you are searching the range of possible speeds, and feasibility is monotone.",
    "time": "O(n log(max pile))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Koko eats from one pile per hour at speed `k` bananas/hour; a pile smaller
than `k` still costs a whole hour. Find the smallest `k` that finishes every
pile within `h` hours.

Ask: can she eat from more than one pile per hour (**no** — that restriction is
what makes the cost a ceiling division); is `h >= len(piles)` guaranteed (yes,
or the problem is infeasible).
""",
        ),
        (
            "Brute force",
            """
Try every speed from 1 to `max(piles)`, checking each in O(n): O(n · max).
With piles up to 10⁹, that is hopeless — and stating the number is what
motivates the search.
""",
        ),
        (
            "The insight",
            """
**Feasibility is monotone.** If speed `s` finishes in time, so does `s + 1` —
eating faster never takes longer.

So the feasible speeds form a *suffix* of the range `[1, max(piles)]`, and you
can binary search for where that suffix starts. You are searching the **answer
space**, not the array; the array only appears inside the feasibility check.

That reframing is the whole pattern, and once you see it a family of problems
that look like hard DP collapses into fifteen lines.
""",
        ),
        (
            "The predicate",
            """
`sum(ceil(pile / speed)) <= h`.

Use `math.ceil(pile / speed)` or `-(-pile // speed)`. Plain integer division
silently undercounts partial piles and gives a speed that is too low — it
passes the sample and fails the judge.
""",
        ),
        (
            "The bounds",
            """
Low is **1** (she must eat something), high is **max(piles)** (eating faster
than the biggest pile buys nothing, since she can only take one pile per
hour).

Justify both out loud. Interviewers probe here, because a candidate who writes
`[1, 10**9]` by reflex usually has not understood why the search is valid.
""",
        ),
        (
            "Dry run",
            """
`piles = [3,6,7,11], h = 8`.

- Try 6: hours 1+1+2+2 = 6 ≤ 8 → feasible, search lower.
- Try 3: 1+2+3+4 = 10 > 8 → infeasible, search higher.
- Try 4: 1+2+2+3 = **8 ≤ 8** → feasible.

Answer 4. Note the exact tie at 8 — that is the boundary the `<=` handles, and
worth pointing at.
""",
        ),
        (
            "Follow-ups",
            """
Every problem in this family is the same three steps. Capacity to Ship
Packages, Split Array Largest Sum, Minimum Number of Days to Make m Bouquets,
Magnetic Force Between Two Balls — write `feasible`, pick the bounds, run the
lower-bound template.
""",
        ),
    ],
}


def min_eating_speed(piles: list[int], hours: int) -> int:
    def feasible(speed: int) -> bool:
        # Ceiling division: a partial pile still costs a whole hour.
        return sum(math.ceil(pile / speed) for pile in piles) <= hours

    low, high = 1, max(piles)
    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid  # works; look for something smaller
        else:
            low = mid + 1

    return low


CASES = [
    (([3, 6, 7, 11], 8), 4),
    (([30, 11, 23, 4, 20], 5), 30),
    (([30, 11, 23, 4, 20], 6), 23),
    (([1], 1), 1),
    (([1000000000], 2), 500000000),
    (([312884470], 968709470), 1),
]


def solve(piles: list[int], hours: int) -> int:
    return min_eating_speed(piles, hours)
