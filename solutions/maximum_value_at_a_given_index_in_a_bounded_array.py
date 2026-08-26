"""Maximum Value at a Given Index in a Bounded Array — LeetCode 1802."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Fix the peak, and the cheapest legal array is forced: ramp down by one each step until you hit the floor of 1.",
    "time": "O(log maxSum)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Build an array of `n` **positive** integers where adjacent entries differ by at
most 1 and the total is at most `maxSum`. Maximise `nums[index]`.

Two constraints do all the work and both are easy to skim past: entries are
`>= 1` (not `>= 0`), and the difference bound is on **absolute** difference, so
the array may rise as well as fall. Restate both before coding.
""",
        ),
        (
            "The insight",
            """
Guess the peak value `v` and ask: what is the **cheapest** array with
`nums[index] == v`? It is forced. Walking away from the peak, each entry should
drop by exactly 1 — dropping faster is illegal, dropping slower costs more —
until it hits the floor of 1, after which every remaining entry is 1.

So the minimum cost of a peak `v` is a closed form per side:

- if the side is shorter than `v − 1`, it is the arithmetic run
  `v−1, v−2, …, v−length`, summing to `(2v − 1 − length) · length / 2`;
- otherwise it is `1 + 2 + … + (v−1)` plus a tail of `length − (v − 1)` ones.

`cost(v)` is strictly increasing in `v`, so binary search the largest `v` with
`cost(v) <= maxSum`. Because we want the **largest** feasible value, bias the
midpoint up (`(low + high + 1) // 2`) and move `low = mid` on success —
otherwise the loop hangs when `high == low + 1`.

Bounds: `low = 1` (entries are positive, and `maxSum >= n` guarantees the
all-ones array fits), `high = maxSum` (the peak alone cannot exceed the budget).
""",
        ),
        (
            "Where it goes wrong",
            """
- **Forgetting the floor of 1.** Letting the ramp run into 0 and negatives
  makes `cost(v)` non-monotone — it starts *decreasing* for large `v` — and the
  binary search returns garbage. The clamp is the whole problem.
- **Double-counting the peak.** `cost = v + left(v) + right(v)` where each side
  excludes the index itself. Left length is `index`, right length is
  `n − index − 1`. Off by one here and `n = 1` breaks immediately.
- **Overflow.** In C++/Java, `cost(v)` with `v` near `10⁹` and a long ramp
  overflows a 32-bit int well before it exceeds `maxSum`. Use 64-bit, or cap
  the ramp length. Python does not care, but the interviewer will ask.
- **`n = 1`.** Left and right are both empty; the answer is exactly `maxSum`.
  Cheap sanity check on your side-sum helper.
""",
        ),
    ],
}


def max_value(n: int, index: int, max_sum: int) -> int:
    def side_sum(peak: int, length: int) -> int:
        """Cheapest cost of `length` entries beside a peak of `peak`."""
        if length <= 0:
            return 0
        if peak - 1 >= length:  # the ramp never reaches the floor
            top, bottom = peak - 1, peak - length
            return (top + bottom) * length // 2
        ramp = (peak - 1) * peak // 2  # peak-1 down to 1
        return ramp + (length - (peak - 1))  # then a tail of 1s

    def cost(peak: int) -> int:
        return peak + side_sum(peak, index) + side_sum(peak, n - index - 1)

    low, high = 1, max_sum
    while low < high:
        mid = (low + high + 1) // 2  # bias up: we assign low = mid
        if cost(mid) <= max_sum:
            low = mid
        else:
            high = mid - 1

    return low


CASES = [
    ((4, 2, 6), 2),
    ((6, 1, 10), 3),
    ((3, 2, 18), 7),
    ((4, 0, 4), 1),
    ((5, 2, 100), 21),
    ((1, 0, 1), 1),
    ((1, 0, 1000000000), 1000000000),
]


def solve(n: int, index: int, max_sum: int) -> int:
    return max_value(n, index, max_sum)
