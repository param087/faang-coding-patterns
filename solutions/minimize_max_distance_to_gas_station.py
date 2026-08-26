"""Minimize Max Distance to Gas Station — LeetCode 774."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Binary search the answer as a real number: a candidate spacing tells you exactly how many stations each gap needs.",
    "time": "O(n · log(range / eps)) — about 100 sweeps",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — described in my own
words: you are given the sorted positions of existing gas stations on a line
and may add `k` more **anywhere**, including at non-integer positions. Minimise
the largest distance between two adjacent stations, and return it as a real
number (judged to 10⁻⁶).

The clarifying question that changes everything: **must new stations sit at
integer positions?** No. Real-valued placement is what makes a gap of length
`g` split by `t` stations give exactly `g / (t + 1)` everywhere — no
remainders, no rounding.
""",
        ),
        (
            "The insight",
            """
The obvious greedy — repeatedly put a station in the currently widest gap, via
a max-heap keyed on `gap / (parts + 1)` — is correct and O((n + k) log n). It
is also a trap at k = 10⁶: it is fine in Python but the constant is heavy, and
it does not generalise to real-valued targets.

Binary search the **answer itself**, as a float. If the largest spacing may be
at most `d`, then a gap of length `g` needs `ceil(g / d) − 1` extra stations,
and those needs are independent across gaps. So:

```
feasible(d)  ⟺  sum(ceil(g / d) - 1 for g in gaps) <= k
```

which is one linear sweep. Monotone, obviously: a larger `d` never needs more
stations. Search `d` over `(0, max(gaps)]`.

Because the domain is real, the loop is not `low < high` — you run a **fixed
number of iterations**. 100 halvings of a range under 10⁸ takes the interval
far below 10⁻⁶ (it bottoms out at double precision long before that), so 100 is
a safe constant that never depends on the input. Reviewers prefer this to
`while high - low > 1e-6`, which can loop forever if `eps` is smaller than the
representable gap near large values.
""",
        ),
        (
            "The floor/ceiling subtlety",
            """
The count is written `int(g / d)`, which is `floor`, not `ceil(g / d) − 1`.
They differ in exactly one case: when `g / d` is a whole number, `floor`
returns one **more** than actually needed.

That over-count is harmless and deliberate. It makes the predicate strict —
feasible on `(answer, ∞)` rather than `[answer, ∞)` — and a real-valued binary
search converges to the infimum either way. Trying to be exact with floats is
worse: `ceil(g / d)` on floats is at the mercy of whether `6.0 / 2.0` lands at
`2.9999999996` or `3.0000000001`, and that flips the count by one right at the
boundary you care about.

Two more things that decide this problem:

- **Return `high`, not `low`.** `high` is always a feasible spacing; `low` is
  always infeasible. Returning the infeasible end is off by one interval width
  in the wrong direction.
- **Gaps, not positions.** Only the `n − 1` differences matter; the absolute
  coordinates never enter the check. If the input arrives unsorted, sort it
  first — the problem promises sorted, but that promise is worth confirming.
""",
        ),
    ],
}


def minmax_gas_dist(stations: list[int], k: int) -> float:
    gaps = [b - a for a, b in zip(stations, stations[1:], strict=False)]
    if not gaps:
        return 0.0

    def feasible(spacing: float) -> bool:
        # floor(gap / spacing) == ceil(gap / spacing) - 1 unless it divides
        # exactly, where it over-counts by one — harmless, and float-safe.
        return sum(int(gap / spacing) for gap in gaps) <= k

    low, high = 0.0, float(max(gaps))
    for _ in range(100):  # fixed iteration count: the domain is real, not integral
        mid = (low + high) / 2
        if mid == 0.0:
            break
        if feasible(mid):
            high = mid
        else:
            low = mid

    return high  # high is the feasible end; low is not


CASES = [
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 9), 0.5),
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1), 1.0),
    (([23, 24, 36, 39, 46, 56, 57, 65, 84, 98], 1), 14.0),
    (([0, 10], 1), 5.0),
    (([0, 10], 4), 2.0),
    (([0, 3, 9], 2), 3.0),
    (([5], 3), 0.0),
]


def solve(stations: list[int], k: int) -> float:
    return round(minmax_gas_dist(list(stations), k), 5)
