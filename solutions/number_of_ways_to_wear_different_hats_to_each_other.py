"""Number of Ways to Wear Different Hats to Each Other — LeetCode 1434."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Bitmask the 10 people, not the 40 hats: iterate over hats and let each one either sit out or dress one uncovered person.",
    "time": "O(H · 2ⁿ · n) — 40 · 1024 · 10 ≈ 4·10⁵",
    "space": "O(2ⁿ)",
    "sections": [
        (
            "What it asks",
            """
`hats[i]` lists the hat types person `i` is willing to wear. Every person must
end up wearing exactly one hat, and **no two people may wear the same hat
type**. Count the assignments, modulo 10⁹+7.

It is a perfect-matching count on a bipartite graph — people on one side, hat
types on the other — which is the permanent of a 0/1 matrix and #P-hard in
general. What makes it tractable is buried in the constraints: **at most 10
people**, hats numbered 1…40. Read those numbers before choosing a state; they
are the whole problem.
""",
        ),
        (
            "The insight",
            """
The instinctive state is "person by person, which hats are already taken" —
and that needs a bitmask over **40** hats. 2⁴⁰ is 10¹², dead on arrival.

Flip the roles. Iterate over **hats** and bitmask the **people**: 2¹⁰ = 1024
states. The asymmetry in the constraints is a deliberate signal — when one side
of a matching is tiny and the other is large, put the mask on the tiny side and
loop over the large one.

```
dp[mask] = number of ways to have dressed exactly the people in `mask`
           using only hats 1..h
```

Processing hat `h`, each state branches two ways: **nobody wears `h`** (carry
`dp[mask]` forward), or **one still-undressed person who likes `h` wears it**
(add `dp[mask]` into `dp[mask | bit]`). Since a hat is considered exactly once,
it can never be issued twice — which is precisely the constraint that a
people-first formulation needs the 40-bit mask to enforce.

Answer: `dp[(1 << n) - 1]`.

The "carry forward" is why hats must be the outer loop and why the update is a
0/1-knapsack: either copy into a fresh array per hat (done here, and the
easiest version to defend), or update the mask loop **downwards** in place so a
hat cannot cascade into itself.

Invert the adjacency first — `people_for_hat[h]` — so the inner loop touches
only the people who can actually wear `h`.
""",
        ),
        (
            "Edge cases and the traps",
            """
- **Two people, one hat type each, the same type** → 0. The mask can never
  fill, and `dp[full]` stays 0 with no special case.
- **More people than distinct acceptable hats** → 0 by the same mechanism;
  do not bother with a Hall's-theorem pre-check.
- **Duplicate hat ids inside one person's list.** LeetCode guarantees they are
  distinct; if they were not, the same person would be counted twice for the
  same hat. Dedupe when building `people_for_hat` if you cannot rely on it.
- **Take the modulus inside the inner loop**, not once at the end. The counts
  reach 40!/(30!) scale before reduction, and in a fixed-width language that
  overflows long before the return.
- **Hats are 1-indexed** and go to 40, so size the bucket array 41 or offset by
  one. An off-by-one here shows up as a silent zero.
- **Do not iterate people on the outside.** A "for each person, for each hat
  they like" loop with a people-mask double-counts, because the same hat can be
  reached in two different orders. Order matters only through the hat loop.
- **Follow-up: at most 10 hats and 40 people?** Then mask the hats and loop the
  people — the same code with the roles swapped, which is the answer that shows
  you understood *why* the flip works rather than that it works.
- **Follow-up: maximise a weight instead of counting?** Replace `+` with `max`
  and the ways-count with a value; the state is unchanged. That is the
  assignment problem, also solvable in O(n³) by Hungarian for larger `n`.
""",
        ),
    ],
}

MOD = 10**9 + 7
MAX_HAT = 40


def number_ways(hats: list[list[int]]) -> int:
    n = len(hats)
    if n == 0:
        return 1  # the empty assignment; LeetCode always sends at least one

    # Invert the adjacency: which people would accept each hat.
    people_for_hat: list[list[int]] = [[] for _ in range(MAX_HAT + 1)]
    for person, owned in enumerate(hats):
        for hat in owned:
            people_for_hat[hat].append(person)

    full = (1 << n) - 1
    dp = [0] * (full + 1)  # dp[mask] = ways to have dressed exactly `mask`
    dp[0] = 1

    for hat in range(1, MAX_HAT + 1):
        candidates = people_for_hat[hat]
        if not candidates:
            continue
        nxt = dp[:]  # branch 1: this hat goes unused
        for mask in range(full + 1):
            ways = dp[mask]
            if ways == 0:
                continue
            for person in candidates:  # branch 2: hand it to one free person
                bit = 1 << person
                if mask & bit:
                    continue
                nxt[mask | bit] = (nxt[mask | bit] + ways) % MOD
        dp = nxt

    return dp[full]


CASES = [
    (([[3, 4], [4, 5], [5]],), 1),
    (([[3, 5, 1], [3, 5]],), 4),
    (([[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],), 24),
    (([[1, 2, 3], [2, 3, 5, 6], [1, 3, 7, 9], [1, 8, 9], [2, 5, 7]],), 111),
    (([[1, 2], [2, 1]],), 2),
    (([[1], [1]],), 0),  # collision: unsatisfiable
    (([[1, 2], [1, 2], [1, 2]],), 0),  # three people, two hats
    (([[40]],), 1),  # the top of the hat range
]


def solve(hats: list[list[int]]) -> int:
    return number_ways(hats)
