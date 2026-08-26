"""Climbing Stairs — LeetCode 70."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "The last move was either a 1-step or a 2-step, so ways(n) = ways(n-1) + ways(n-2) — Fibonacci in disguise.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
You climb a staircase of `n` steps taking 1 or 2 steps at a time. Count the
distinct orderings of moves that reach the top.

Ask whether **order matters** — it does, `1+2` and `2+1` are two ways. If it
did not, the answer would be `n//2 + 1` and this would not be a DP question.
That one clarification separates this from a counting-partitions problem.
""",
        ),
        (
            "The insight",
            """
Classify by the **last move**. Every route to step `n` ends with either a
1-step (arriving from `n-1`) or a 2-step (arriving from `n-2`), and those two
sets are disjoint and cover everything. So

```
ways(n) = ways(n-1) + ways(n-2),  ways(0) = ways(1) = 1
```

That is Fibonacci shifted by one. Say "classify by the last move" out loud —
it is the reusable move, and it is what you will reach for again on Decode
Ways and Combination Sum IV.

Writing this as plain recursion is the trap: `ways(45)` without memoisation is
roughly 2·10⁹ calls. Only two values are ever read, so keep two variables and
walk up in O(n) time, O(1) space.
""",
        ),
        (
            "Follow-ups",
            """
- **"n up to 10¹⁸?"** Fibonacci by matrix power or fast doubling, O(log n)
  multiplications. Worth naming even if you never write it.
- **Steps of size 1..k** — same recurrence over a sliding window of the last
  `k` values, O(nk), or O(n) keeping a running total of the window.
- **Some steps are broken** — set `ways(i) = 0` at those indices, which is
  exactly the Min Cost Climbing Stairs / Jump Game family.
- **Base case convention:** `ways(0) = 1` (one way to stand still). Getting
  that wrong shifts the entire sequence by one, and it is the single most
  common bug here.
""",
        ),
    ],
}


def climb_stairs(n: int) -> int:
    # one_back = ways(i-1), two_back = ways(i-2); ways(0) = ways(1) = 1
    two_back, one_back = 1, 1

    for _ in range(2, n + 1):
        two_back, one_back = one_back, one_back + two_back

    return one_back


CASES = [
    ((0,), 1),
    ((1,), 1),
    ((2,), 2),
    ((3,), 3),
    ((4,), 5),
    ((5,), 8),
    ((10,), 89),
    ((45,), 1836311903),
]


def solve(n: int) -> int:
    return climb_stairs(n)
