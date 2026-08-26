"""Sqrt(x) — LeetCode 69."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "`mid * mid <= x` is monotone in mid, so the integer square root is a boundary search over [1, x // 2] — no floats anywhere.",
    "time": "O(log x)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return ⌊√x⌋ for a non-negative integer `x`, without any built-in square root.
The fractional part is truncated, so `sqrt(8) == 2`.

The banned built-in is the entire question: it is a test of whether you can
binary search a **monotone predicate** over an integer range rather than an
array. Confirm the input is non-negative (it is) and that the output is an
integer (it is — no rounding-up trap).
""",
        ),
        (
            "The insight",
            """
`mid * mid <= x` is false for every `mid` above the answer and true for every
`mid` at or below it. One flip, so binary search finds it.

Bounds worth justifying rather than guessing:

- **Low is 1**, after returning `x` directly for `x < 2` (0 and 1 are their own
  roots, and they are the only inputs where `x // 2` collapses below 1).
- **High is `x // 2`**, because for `x >= 4` the root is never more than half
  of `x`. `x = 10⁹` starts the search at 5·10⁸ instead of 10⁹ — one iteration
  saved, but the real value is that you can defend the bound.

Everything is integer arithmetic. `mid * mid` in Python cannot overflow; in
Java or C++ it does, and you would write `mid <= x / mid` instead. Say that.
""",
        ),
        (
            "The off-by-one, and why floats fail",
            """
The loop uses the closed range `[low, high]` with `while low <= high`. On exit
`high` has landed on the largest value whose square is `<= x`, so **return
`high`, not `low`** — `low` is one past it. That single line is where this
question is failed.

Trace `x = 8`: `high` starts at 4, `mid = 2` gives 4 < 8 so `low = 3`;
`mid = 3` gives 9 > 8 so `high = 2`; loop ends with `low = 3 > high = 2`,
return **2**. Correct.

And the tempting one-liner, `int(math.sqrt(x))`: it is wrong for large inputs.
Doubles carry 53 bits of mantissa, so past 2⁵³ the division of the number line
is coarser than 1 and the result gets rounded to a representable neighbour.
`x = 67108865² − 1 = 4503599761588224` has true root 67108864, but
`math.sqrt(x)` returns exactly `67108865.0` and the truncation hands back a
value **one too big**. LeetCode caps `x` at 2³¹ − 1 so it happens to pass
there; the honest Python answer is `math.isqrt`, and the honest interview
answer is this loop.

Edge cases that matter: `x = 0` → 0, `x = 1` → 1 (both short-circuited),
`x = 2147395599` → 46339 (the classic "is your bound off by one" input, since
46340² = 2147395600 is one too big).
""",
        ),
    ],
}


def my_sqrt(x: int) -> int:
    if x < 2:
        return x  # 0 and 1 are their own roots; also keeps x // 2 >= 1 below

    low, high = 1, x // 2  # for x >= 4 the root never exceeds x // 2

    while low <= high:
        mid = (low + high) // 2
        square = mid * mid
        if square == x:
            return mid
        if square < x:
            low = mid + 1
        else:
            high = mid - 1

    return high  # largest value whose square is <= x; low is one past it


CASES = [
    ((0,), 0),
    ((1,), 1),
    ((2,), 1),
    ((4,), 2),
    ((8,), 2),
    ((15,), 3),
    ((16,), 4),
    ((2147395599,), 46339),
    ((2147483647,), 46340),
]


def solve(x: int) -> int:
    return my_sqrt(x)
