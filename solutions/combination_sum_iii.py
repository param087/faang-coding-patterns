"""Combination Sum III — LeetCode 216."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "The candidate set is fixed at 1–9 and each digit is used at most once, so this is subsets of a 9-element set with two arithmetic prunes.",
    "time": "O(C(9, k) · k) — at most 126 combinations copied out",
    "space": "O(k) recursion depth, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Choose exactly `k` distinct digits from `1`–`9` that sum to `n`. Return every
such combination; each digit may be used at most once and combinations are sets,
so `[1,2,4]` and `[2,1,4]` are the same answer.

The distinction worth naming out loud: **Combination Sum** (39) reuses values and
recurses with `i`; **Combination Sum II** (40) has duplicates in the input and
needs a same-depth skip; this one has a fixed, duplicate-free candidate set and
recurses with `i + 1`. Same skeleton, three different one-line changes.

The whole search space is 2⁹ = 512 subsets, so brute force is legitimate here.
The pruning is what an interviewer is actually testing.
""",
        ),
        (
            "The insight",
            """
Passing `digit + 1` to the recursive call is what enforces "each digit at most
once" **and** kills permutation duplicates in one stroke: every path is strictly
increasing, so each set is generated exactly once. No `visited` array, no sort,
no dedup pass.

On top of that, two arithmetic bounds turn the tree from 512 nodes into a
handful. With `slots = k - len(path)` digits still to place:

- **Smallest reachable total** from `digit` upward is
  `digit·slots + slots(slots−1)/2` — that is `digit + (digit+1) + …`. Once that
  exceeds what remains, every later digit is worse, so `break`.
- **Largest reachable total** with `slots` digits is `9 + 8 + …`. If what remains
  exceeds it, this branch cannot be saved by any choice, so `return` immediately.

The second one is the one candidates forget, and it is the one that makes
`(k=3, n=24)` finish without exploring the low digits at all.
""",
        ),
        (
            "Edge cases",
            """
- **`k > 9`** — impossible, there are only nine digits. Guard it, or
  `sum(range(10 - slots, 10))` starts computing nonsense for `slots > 9`.
- **`n > 45`** — 45 is `1+…+9`, so anything larger is `[]`. The upper-bound
  prune already returns this on the first call; the guard just makes it obvious.
- **`n` too small**, e.g. `k = 4, n = 1`: the lower-bound prune breaks on the
  first digit and you return `[]` without recursing.
- **`k = 9`** has exactly one candidate, `[1..9]`, and it works only for
  `n = 45`.

Sorted output falls out for free from the increasing-path invariant, so if the
grader wants a canonical order you have nothing to do. Complexity is bounded by
C(9, k) ≤ 126, so quoting "exponential" here is technically true and unhelpful —
quote the constant.
""",
        ),
    ],
}


def combination_sum3(k: int, n: int) -> list[list[int]]:
    if not 1 <= k <= 9:
        return []

    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int, remaining: int) -> None:
        slots = k - len(path)
        if slots == 0:
            if remaining == 0:
                result.append(path[:])  # a copy — `path` is mutated below
            return
        # Largest total still reachable: 9 + 8 + ... with `slots` digits.
        if remaining > sum(range(10 - slots, 10)):
            return

        for digit in range(start, 10):
            # Smallest total from `digit` upward: digit + (digit+1) + ...
            if digit * slots + slots * (slots - 1) // 2 > remaining:
                break
            path.append(digit)
            explore(digit + 1, remaining - digit)
            path.pop()

    explore(1, n)
    return result


CASES = [
    ((3, 7), [[1, 2, 4]]),
    ((3, 9), [[1, 2, 6], [1, 3, 5], [2, 3, 4]]),
    ((4, 1), []),  # lower bound breaks on the first digit
    ((2, 18), []),  # 9 + 8 = 17 is the most two digits can reach
    ((9, 45), [[1, 2, 3, 4, 5, 6, 7, 8, 9]]),
    ((1, 5), [[5]]),
    ((10, 45), []),  # only nine digits exist
    (
        (3, 15),
        [
            [1, 5, 9],
            [1, 6, 8],
            [2, 4, 9],
            [2, 5, 8],
            [2, 6, 7],
            [3, 4, 8],
            [3, 5, 7],
            [4, 5, 6],
        ],
    ),
]


def solve(k: int, n: int) -> list[list[int]]:
    return combination_sum3(k, n)
