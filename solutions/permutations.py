"""Permutations — LeetCode 46."""

from __future__ import annotations

from math import factorial

META = {
    "pattern": "backtracking",
    "insight": "Unlike subsets there is no `start` index — every unused value is a candidate at every depth, and only leaves are answers.",
    "time": "O(n · n!)",
    "space": "O(n) for the recursion and the used-set, excluding the output",
    "sections": [
        (
            "What it asks",
            """
All orderings of a list of **distinct** integers, in any output order.

Confirm the distinctness — with duplicates it is Permutations II and needs a
different skip rule. `n ≤ 8` in the constraints is not decoration: 8! = 40320,
and it tells you enumeration is the intended answer rather than a clever
formula.
""",
        ),
        (
            "The insight",
            """
Permutations differ from subsets in exactly two places, and naming both is the
answer an interviewer is listening for:

- **No `start` index.** A subset never revisits an earlier element, so the loop
  runs from `start`. A permutation uses *every* element, just in a different
  order, so the loop runs over the whole array and a `used` set decides what is
  still available.
- **Only leaves count.** Subsets record at every node; here you record when
  `len(path) == n`, because a partial arrangement is not a permutation.

The branching factor falls as you descend — n choices, then n−1, then n−2 —
which is where n! comes from. Multiply by the O(n) copy at each of the n!
leaves for O(n · n!). At n = 8 that is roughly 3 × 10⁵ element copies:
instantaneous. At n = 12 it is 5 × 10⁹, which is the constraint you should ask
about before writing anything.
""",
        ),
        (
            "Two ways to track availability",
            """
The `used` set above costs O(n) extra space and leaves the input untouched.
The alternative is the **swap** formulation: at depth `d`, swap each of
`nums[d:]` into position `d`, recurse, swap back. It allocates nothing beyond
the recursion and the output.

The trap in the swap version is that it does **not** produce lexicographic
order, and it is genuinely awkward to extend to Permutations II — the "skip
equal siblings" rule needs a per-level seen-set because the array is no longer
sorted after the first swap. If duplicates might turn up in a follow-up, the
`used` version is the one to write.

`itertools.permutations` exists and is a fine one-liner to mention, but write
the recursion: the question is about the recursion.
""",
        ),
    ],
}


def permute(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

    def explore() -> None:
        if len(path) == len(nums):
            result.append(path[:])  # a copy — `path` keeps mutating
            return
        for i, value in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            path.append(value)
            explore()
            path.pop()
            used[i] = False

    explore()
    return result


def permute_by_swapping(nums: list[int]) -> list[list[int]]:
    """No `used` array: rotate each remaining value into place, then undo."""
    working = nums[:]  # `solve` must stay pure
    result: list[list[int]] = []

    def explore(depth: int) -> None:
        if depth == len(working):
            result.append(working[:])
            return
        for i in range(depth, len(working)):
            working[depth], working[i] = working[i], working[depth]
            explore(depth + 1)
            working[depth], working[i] = working[i], working[depth]

    explore(0)
    return result


CASES = [
    (([1, 2, 3],), [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
    (([0, 1],), [[0, 1], [1, 0]]),
    (([-1, 0],), [[-1, 0], [0, -1]]),
    (([1],), [[1]]),
    (([],), [[]]),
]


def solve(nums: list[int]) -> list[list[int]]:
    return permute(nums)


def check() -> None:
    for args, expected in CASES:
        assert permute(*args) == expected

    # Both formulations enumerate the same n! arrangements, in different orders.
    for size in range(7):
        values = list(range(size))
        by_used = permute(values)
        by_swap = permute_by_swapping(values)
        assert len(by_used) == factorial(size)
        assert sorted(by_used) == sorted(by_swap)
        assert len({tuple(p) for p in by_used}) == factorial(size)
