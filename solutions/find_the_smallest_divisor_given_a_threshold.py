"""Find the Smallest Divisor Given a Threshold — LeetCode 1283."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "The sum of ceiling divisions falls as the divisor grows, so the acceptable divisors are a suffix — binary search where it starts.",
    "time": "O(n log(max num))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Pick the smallest positive integer `d` such that
`sum(ceil(num / d) for num in nums) <= threshold`.

This is Koko Eating Bananas (875) with the story stripped out, which makes it
the cleanest possible statement of the pattern — and a common warm-up before a
harder variant. If you recognise it, say so; interviewers like hearing the
family named.
""",
        ),
        (
            "The insight",
            """
`f(d) = sum(ceil(num / d))` is **non-increasing** in `d`. Every term either
stays put or drops when the divisor grows, so the whole sum does. That gives
monotonicity for free, and the acceptable divisors form a suffix of
`[1, max(nums)]`.

Bounds worth justifying:

- **low = 1** — the smallest legal divisor, giving `f(1) = sum(nums)`, the
  largest possible value.
- **high = max(nums)** — at that divisor every term is already 1, so
  `f = len(nums)`, and no larger divisor can do better. Since the problem
  guarantees `threshold >= len(nums)`, the high end is always feasible and the
  search cannot fall off the end.

That guarantee is exactly why no `-1` case exists. If the interviewer drops it,
you need an explicit `if len(nums) > threshold: return -1` first.
""",
        ),
        (
            "The ceiling trap",
            """
`ceil` is the whole problem. `num // d` silently rounds down, which
**undercounts** the sum, which makes small divisors look acceptable, which
returns an answer that is too small. It passes the samples and fails the
judge — the worst kind of bug.

Three safe spellings, in order of preference under interview conditions:

```python
-(-num // d)          # integer only, no float, no import
(num + d - 1) // d    # the C++/Java idiom; watch overflow in those languages
math.ceil(num / d)    # readable, but goes through a float
```

The float version is fine here (`num <= 10⁶`), but with 64-bit inputs
`num / d` loses precision above 2⁵³ and the answer goes wrong by one. Reach for
`-(-num // d)` by default and you never have to think about it again.
""",
        ),
    ],
}


def smallest_divisor(nums: list[int], threshold: int) -> int:
    def total(divisor: int) -> int:
        return sum(-(-num // divisor) for num in nums)  # ceiling, no floats

    low, high = 1, max(nums)
    while low < high:
        mid = (low + high) // 2
        if total(mid) <= threshold:
            high = mid  # acceptable; look for a smaller divisor
        else:
            low = mid + 1

    return low


CASES = [
    (([1, 2, 5, 9], 6), 5),
    (([44, 22, 33, 11, 1], 5), 44),
    (([2, 3, 5, 7, 11], 11), 3),
    (([19], 5), 4),
    (([1], 1), 1),
    (([1000000], 1), 1000000),
    (([1, 1, 1, 1], 4), 1),
]


def solve(nums: list[int], threshold: int) -> int:
    return smallest_divisor(nums, threshold)
