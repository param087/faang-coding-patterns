"""Subsets — LeetCode 78."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Choose, explore, un-choose — and record at every node, not just the leaves.",
    "time": "O(n · 2ⁿ)",
    "space": "O(n) for the recursion, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Return the power set — every subset of the input, in any order.

Ask: are values distinct (if not, it is Subsets II and needs a dedup); must
the empty subset be included (yes); does the output order matter (no).
""",
        ),
        (
            "The template",
            """
Choose, explore, un-choose. Every backtracking problem is these three lines in
a loop; what changes is where you record and what you prune.

For subsets, **every node of the recursion tree is an answer**, so you record
on entry rather than at a leaf. Compare with permutations, where only complete
arrangements count.
""",
        ),
        (
            "The one-character bug",
            """
`result.append(path[:])`, not `result.append(path)`.

Appending `path` itself stores a **reference** that the next `pop()` mutates.
Every entry in the result ends up as the same empty list. It is a
one-character bug with a spectacular failure mode, and it is worth writing the
slice deliberately.
""",
        ),
        (
            "The complexity, stated honestly",
            """
O(n · 2ⁿ), **not** O(2ⁿ).

There are 2ⁿ subsets, and each one costs O(n) to copy into the output.
Claiming O(2ⁿ) ignores the copy, and interviewers notice.
""",
        ),
        (
            "The other solution",
            """
Count from `0` to `2ⁿ − 1` and read each integer as a membership mask: bit `i`
means "include `nums[i]`".

Offering this shows you see the correspondence between subsets and binary
numbers — which is exactly why a constraint of `n ≤ 20` signals
[bitmask](../../patterns/bit-manipulation/) approaches.
""",
        ),
        (
            "Follow-ups",
            """
- **Subsets II** — duplicates in the input. Sort, then skip repeats at the
  same depth with `if i > start and nums[i] == nums[i-1]`. Note `i > start`,
  **not** `i > 0`: the first occurrence at each level must be allowed through.
- **Combination Sum** — the same skeleton, passing `i` instead of `i + 1` so
  values can be reused.
- **Subsets summing to a target** — add a pruning condition, which is where
  backtracking earns its keep over enumeration.
""",
        ),
    ],
}


def subsets(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int) -> None:
        result.append(path[:])  # a copy — `path` is mutated below
        for i in range(start, len(nums)):
            path.append(nums[i])  # choose
            explore(i + 1)  # explore
            path.pop()  # un-choose

    explore(0)
    return result


def subsets_via_bits(nums: list[int]) -> list[list[int]]:
    """The bitmask alternative: each integer 0..2^n-1 *is* a subset."""
    n = len(nums)
    return [[nums[i] for i in range(n) if mask & (1 << i)] for mask in range(1 << n)]


CASES = [
    (([1, 2, 3],), [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]),
    (([0],), [[], [0]]),
    (([1, 2],), [[], [1], [1, 2], [2]]),
    (([],), [[]]),
]


def solve(nums: list[int]) -> list[list[int]]:
    return subsets(nums)


def check() -> None:
    for args, expected in CASES:
        assert subsets(*args) == expected
        # Both formulations must produce the same set of subsets.
        assert sorted(map(tuple, subsets_via_bits(*args))) == sorted(map(tuple, expected))
