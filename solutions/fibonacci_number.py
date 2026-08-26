"""Fibonacci Number — LeetCode 509."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "The naive recursion recomputes the same subproblems exponentially often; two rolling variables replace the whole table.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
`F(0) = 0`, `F(1) = 1`, `F(n) = F(n-1) + F(n-2)`. Return `F(n)`.

Nobody asks this to see whether you know Fibonacci. They ask it as the
warm-up that establishes vocabulary — memoisation, tabulation, rolling state —
before the real DP question. Treat it as a chance to name all three cleanly in
sixty seconds, then move on.
""",
        ),
        (
            "The insight",
            """
The recursion tree for plain `fib(n-1) + fib(n-2)` has about `F(n+1)` leaves,
so it is Θ(φⁿ) with φ ≈ 1.618. At `n = 50` that is roughly **2·10¹⁰ calls** —
minutes, not milliseconds — and every one of them recomputes a value already
computed somewhere else in the tree.

Three fixes, increasing in polish:

1. **Memoise** the recursion (`@cache`): O(n) time, O(n) space plus O(n) stack.
2. **Tabulate** bottom-up into an array: O(n) time, O(n) space, no stack.
3. **Roll** the table into two variables, because the recurrence only ever
   reads the previous two entries: O(n) time, **O(1) space**.

Step 3 is the habit worth building. Almost every 1-D DP with a fixed-width
lookback folds the same way — House Robber, Climbing Stairs, Min Cost
Climbing Stairs, Decode Ways are all this same fold.
""",
        ),
        (
            "Follow-ups",
            """
- **"Now n = 10¹⁸, modulo 10⁹+7."** O(n) is too slow. Use fast doubling:
  `F(2k) = F(k)·(2F(k+1) − F(k))`, `F(2k+1) = F(k)² + F(k+1)²`, which is
  O(log n) multiplications. Equivalent to raising `[[1,1],[1,0]]` to the `n`th
  power.
- **"Closed form?"** Binet's formula, `(φⁿ − ψⁿ)/√5`, is exact in maths and
  wrong in floating point past about `n = 71` in IEEE doubles. Say that — the
  question is testing whether you know when a formula stops being usable.
- **Python has arbitrary-precision ints**, so nothing overflows here. In Java
  or C++, `F(93)` already exceeds a signed 64-bit integer; that is the
  follow-up worth pre-empting if you are writing in either.
""",
        ),
    ],
}


def fib(n: int) -> int:
    previous, current = 0, 1  # F(0), F(1)

    for _ in range(n):
        previous, current = current, previous + current

    return previous  # after n steps, `previous` holds F(n)


CASES = [
    ((0,), 0),
    ((1,), 1),
    ((2,), 1),
    ((3,), 2),
    ((4,), 3),
    ((10,), 55),
    ((30,), 832040),
    ((50,), 12586269025),
]


def solve(n: int) -> int:
    return fib(n)
