"""Beautiful Arrangement — LeetCode 526."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "backtracking",
    "insight": "Fill the highest position first — position n has the fewest legal values — and memoise on the bitmask of values already used.",
    "time": "O(2ⁿ · n) with memoisation; n ≤ 15 so 2¹⁵ · 15 ≈ 5·10⁵ steps",
    "space": "O(2ⁿ) for the memo table",
    "sections": [
        (
            "What it asks",
            """
Count the permutations `perm` of `1..n` where, for every 1-indexed position `i`,
either `perm[i] % i == 0` or `i % perm[i] == 0`. Return the **count**, not the
arrangements — which is exactly what makes memoisation legal.

`n ≤ 15`. 15! is 1.3·10¹², so enumerating permutations and filtering is out;
2¹⁵ = 32768 is not. That gap is the whole problem.
""",
        ),
        (
            "The insight",
            """
Two decisions, and both matter.

**Fill positions from `n` down to `1`, not upward.** Position `i` accepts only
divisors and multiples of `i`. Position 1 accepts *everything* — every value is
a multiple of 1 — so starting there branches `n` ways immediately and prunes
nothing. Position `n` typically accepts a handful: for `n = 15` only `1, 3, 5,
15`. Same rule as most-constrained-variable ordering in Sudoku: pick the
decision with the fewest options first. On `n = 15` the descending order finishes
in a few milliseconds where ascending grinds.

**Memoise on the set of used values.** The number of ways to complete the
arrangement depends only on *which* values remain, never on the order they were
placed in. Encode "used" as a 15-bit integer and the state space collapses from
15! paths to 2¹⁵ states. The position index is redundant — it equals
`n - popcount(used)` — so it is carried only for readability, and `@cache`
happily keys on both.

That redundancy is worth saying out loud: an interviewer who hears "the depth is
implied by the mask" knows you understand why the memo works.
""",
        ),
        (
            "Follow-ups",
            """
- **"Return the arrangements themselves."** The memo dies — you cannot share a
  cached count across distinct prefixes when the prefix is part of the output.
  You are back to plain backtracking, output-sensitive: `n = 15` has 24679
  arrangements, so listing them is fine, but the complexity statement changes to
  O(answers · n).
- **"Why not precompute the legal (position, value) pairs?"** Do — a list of
  candidate values per position, built once in O(n²), removes the divisibility
  test from the inner loop and is a genuine constant-factor win.
- **Bipartite framing.** Positions on one side, values on the other, an edge when
  the divisibility holds. The answer is the **permanent** of that 0/1 matrix.
  Computing a permanent is #P-complete in general; Ryser's formula gives
  O(2ⁿ · n), which is exactly the bound above — the memoised backtracking *is*
  a permanent computation, and naming that is a strong close.
- **`n = 1` → 1**, and the counts grow unevenly: 1, 2, 3, 8, 10, 36, 41, 132.
  The dip at `n = 7` (41 after 36) surprises people; primes have few divisors, so
  a prime `n` constrains hard.
""",
        ),
    ],
}


def count_arrangement(n: int) -> int:
    if n < 1:
        return 0

    @cache
    def explore(position: int, used: int) -> int:
        if position == 0:
            return 1  # every position filled: one complete arrangement

        total = 0
        for value in range(1, n + 1):
            bit = 1 << (value - 1)
            if used & bit:
                continue
            if value % position and position % value:
                continue  # neither divides the other
            total += explore(position - 1, used | bit)
        return total

    result = explore(n, 0)
    explore.cache_clear()  # the closure captures `n`; do not hold the table
    return result


CASES = [
    ((1,), 1),
    ((2,), 2),
    ((3,), 3),
    ((4,), 8),
    ((5,), 10),
    ((6,), 36),
    ((12,), 4010),
    ((15,), 24679),  # 15! = 1.3e12 paths, 2^15 = 32768 memo states
]


def solve(n: int) -> int:
    return count_arrangement(n)
