"""Minimum Speed to Arrive on Time — LeetCode 1870."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Speed is monotone — going faster never arrives later — so binary search it, and run the arrival check in integers, not floats.",
    "time": "O(n log(max speed))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
`dist[i]` is the length of the i-th train ride, all at the same integer speed.
Every ride except the last must **wait for the next departure on the hour**, so
its cost is `ceil(dist[i] / speed)`. The last ride costs the exact fraction
`dist[-1] / speed`. Return the least integer speed that arrives within `hour`,
or `-1` if no speed does.

Ask: is `hour` an integer? It is not — the constraint says at most two decimal
places, and that detail is the whole problem. Also ask whether speed is bounded
(yes, 10⁷), because that bound is what makes "impossible" decidable.
""",
        ),
        (
            "The insight",
            """
Two observations turn this into the standard template.

**Monotone.** Raising the speed can only shrink each `ceil(dist[i] / speed)`
and the final fraction, so total time is non-increasing in speed. Feasible
speeds are a suffix of `[1, 10⁷]`; binary search for where it starts.

**Impossible is cheap to detect.** The first `n - 1` rides each cost at least
one whole hour no matter how fast you go, plus a positive last leg. So if
`hour <= n - 1` the answer is `-1` immediately. Otherwise check the top of the
range once: if speed 10⁷ misses, nothing makes it. Do not try to reason about
infeasibility inside the loop — check the endpoint and return.

Everything else is `feasible(speed)` plugged into the lower-bound search.
""",
        ),
        (
            "The floating-point trap",
            """
The obvious check is

```python
sum(ceil(d / speed) for d in dist[:-1]) + dist[-1] / speed <= hour
```

and it fails the judge. `dist = [1, 1, 100000], hour = 2.01` needs speed 10⁷,
where the total is exactly `1 + 1 + 0.01 = 2.01`. In binary floating point
`2.01` is stored as slightly more than 2.01 while `100000 / 10**7` rounds to
slightly more than `0.01`, and whether the `<=` holds is a coin toss you do not
control. Worse, `ceil(d / speed)` on a float can round the *wrong side* of an
exact division for large `d`.

Two fixes, both worth naming:

- `ceil` in integers: `-(-d // speed)`, which never touches a float.
- Compare in scaled integers. `hour` has at most two decimals, so
  `round(hour * 100)` is exact, and the whole comparison becomes

```python
(whole_hours * speed + dist[-1]) * 100 <= round(hour * 100) * speed
```

Multiplying through by `speed` clears the last fraction. No floats survive into
the comparison, so the boundary case is decided by arithmetic rather than luck.
""",
        ),
    ],
}

MAX_SPEED = 10**7


def min_speed_on_time(dist: list[int], hour: float) -> int:
    n = len(dist)
    # `hour` has at most two decimal places, so this scaling is exact.
    hour_hundredths = round(hour * 100)

    # The first n - 1 legs each burn a whole hour, and the last leg is positive.
    if hour_hundredths <= (n - 1) * 100:
        return -1

    def feasible(speed: int) -> bool:
        whole = sum(-(-d // speed) for d in dist[:-1])  # integer ceiling
        # (whole + dist[-1]/speed) <= hour, multiplied by 100 * speed.
        return (whole * speed + dist[-1]) * 100 <= hour_hundredths * speed

    if not feasible(MAX_SPEED):
        return -1

    low, high = 1, MAX_SPEED
    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid
        else:
            low = mid + 1

    return low


CASES = [
    (([1, 3, 2], 6), 1),
    (([1, 3, 2], 2.7), 3),
    (([1, 3, 2], 1.9), -1),
    (([1, 3, 2], 2.0), -1),
    (([1, 1, 100000], 2.01), 10000000),
    (([1, 1, 1], 2.99), 2),
    (([1, 1, 1], 3), 1),
    (([5], 1), 5),
]


def solve(dist: list[int], hour: float) -> int:
    return min_speed_on_time(dist, hour)
