"""Perfect Squares — LeetCode 279."""

from __future__ import annotations

from math import isqrt

META = {
    "pattern": "dp-1d",
    "insight": "Unbounded coin change with coins 1, 4, 9, 16, … — and Lagrange's theorem pins the answer to 1, 2, 3 or 4.",
    "time": "O(n√n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
The fewest perfect squares that sum to `n`. Repeats allowed, so `12 = 4+4+4`
is three and not `9+1+1+1`.

Ask whether `n = 0` is possible (LeetCode says `n ≥ 1`, answer 0 by convention)
and how large `n` gets (10⁴ — small enough that the DP is fine, large enough
that exponential recursion is not).

The wrong first answer is greedy: take the biggest square below `n` and recurse.
On `n = 12` that gives 9 + 1 + 1 + 1 = **4**, and the answer is 3. On `n = 18`
it gives 16 + 1 + 1 = 3 and the answer is 2 (9 + 9). Greedy fails because the
coin system is not canonical, which is the same reason it fails for coin change
with `[1, 3, 4]`.
""",
        ),
        (
            "The insight",
            """
This *is* unbounded coin change, with the coin set `{1, 4, 9, …, ⌊√n⌋²}`:

```
dp[i] = 1 + min(dp[i - j*j] for j*j <= i)
```

`dp[0] = 0`, and the loop is O(n√n) — at n = 10⁴ that is about 10⁶ operations,
comfortably instant.

Two things make this the right frame rather than a coincidence:

- The coin count is only **√n ≈ 100** for n = 10⁴, not n, so the inner loop is
  cheap.
- The order of the loops does not matter for a *minimum count* (unlike counting
  the number of ways, where the outer loop must be over coins). Nesting `i`
  outside and `j` inside reads naturally and is what you want on a whiteboard.

The BFS phrasing is equally valid and often lands better: nodes are remainders,
edges subtract a square, and the shortest path from `n` to 0 is the answer.
Same complexity; use whichever you can write without a bug.
""",
        ),
        (
            "The four-square shortcut",
            """
**Lagrange's four-square theorem**: every natural number is the sum of at most
four squares. So the answer is always 1, 2, 3 or 4 — never more — which turns
the problem into three cheap tests:

1. `n` is a perfect square → **1**.
2. **Legendre's three-square theorem**: `n` needs four squares *exactly when* it
   has the form `4^a(8b + 7)`. Strip factors of 4, check `n % 8 == 7` → **4**.
3. Try every `a ≤ √n` and test whether `n - a²` is a square → **2**.
4. Otherwise → **3**.

That is O(√n) time and O(1) space. Order matters: test the four-square form
*before* the two-square scan, otherwise you pay the scan on the numbers that
were going to answer 4 anyway.

Sanity checks: `7 = 8·0 + 7` → 4 (`4+1+1+1`). `28 = 4·7` → 4. `43` is not
`4^a(8b+7)` and not a sum of two squares, so **3** (`25 + 9 + 9`). `48 = 16·3`
→ 3 (`16+16+16`).

Say the DP first — it is what the question is testing, and it generalises to any
coin set. Offer the theorem as the follow-up, and be honest that it is a number-
theory fact you are recalling, not deriving at the board.
""",
        ),
    ],
}


def num_squares(n: int) -> int:
    """The DP everyone should write: unbounded coin change over squares."""
    if n <= 0:
        return 0

    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        best = i  # worst case: i copies of 1
        j = 1
        while j * j <= i:
            best = min(best, dp[i - j * j] + 1)
            j += 1
        dp[i] = best

    return dp[n]


def num_squares_theorem(n: int) -> int:
    """O(√n) via Lagrange (answer ≤ 4) plus Legendre (when it is exactly 4)."""
    if n <= 0:
        return 0

    if isqrt(n) ** 2 == n:
        return 1

    stripped = n
    while stripped % 4 == 0:
        stripped //= 4
    if stripped % 8 == 7:  # 4^a(8b + 7) needs all four
        return 4

    for a in range(1, isqrt(n) + 1):
        rest = n - a * a  # rest > 0, since n is not itself a square
        if isqrt(rest) ** 2 == rest:
            return 2

    return 3


CASES = [
    ((12,), 3),
    ((13,), 2),
    ((7,), 4),
    ((28,), 4),
    ((43,), 3),
    ((48,), 3),
    ((1,), 1),
    ((0,), 0),
]


def solve(n: int) -> int:
    return num_squares(n)


def check() -> None:
    for args, expected in CASES:
        assert num_squares(*args) == expected
        assert num_squares_theorem(*args) == expected

    # The two formulations must agree everywhere, not just on the samples.
    for n in range(1, 400):
        assert num_squares(n) == num_squares_theorem(n), n
