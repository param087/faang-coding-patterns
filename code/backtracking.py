"""Backtracking: choose, explore, un-choose.

Every one of these is the same three lines wrapped in a loop. What changes is
the *pruning* — and pruning is the whole difference between a solution that
passes and one that times out.

The two dedup rules are worth memorising because they are not interchangeable:
sort and skip `i > start and nums[i] == nums[i-1]` for duplicate values in the
input; use a `used[]` array when the same index must not be reused.
"""

from __future__ import annotations


def subsets(nums: list[int]) -> list[list[int]]:
    """The power set. The plainest instance of the template."""
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int) -> None:
        result.append(path[:])  # every node is an answer, not just the leaves
        for i in range(start, len(nums)):
            path.append(nums[i])  # choose
            explore(i + 1)  # explore
            path.pop()  # un-choose

    explore(0)
    return result


def subsets_with_duplicates(nums: list[int]) -> list[list[int]]:
    """Power set of a multiset, without duplicate subsets.

    Sorting brings equal values together; the skip then says "at this depth I
    have already tried this value". Note `i > start`, not `i > 0` — the first
    occurrence at each level must be allowed through.
    """
    nums = sorted(nums)
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            explore(i + 1)
            path.pop()

    explore(0)
    return result


def permutations(nums: list[int]) -> list[list[int]]:
    """All orderings.

    Permutations differ from subsets in that every element is used exactly
    once and order matters, so the loop restarts from 0 each time and a
    `used` array does the bookkeeping.
    """
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

    def explore() -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            explore()
            path.pop()
            used[i] = False

    explore()
    return result


def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """Combinations summing to target, values reusable without limit.

    Two prunings, and the sort is what enables the second. Passing `i` rather
    than `i + 1` is what permits reuse — that single character is the
    difference from the subsets template.
    """
    candidates = sorted(candidates)
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break  # sorted, so everything after is too big
            path.append(candidates[i])
            explore(i, remaining - candidates[i])  # `i`, not `i + 1`: reusable
            path.pop()

    explore(0, target)
    return result


def solve_n_queens(n: int) -> list[list[str]]:
    """N-Queens, with O(1) conflict checks.

    Scanning the board for conflicts is O(n) per placement. Three sets make it
    O(1): a column is `c`, a "\\" diagonal is constant in `r - c`, and a "/"
    diagonal is constant in `r + c`. Recognising that diagonals have constant
    sums and differences is the entire optimisation.
    """
    columns: set[int] = set()
    diagonal: set[int] = set()  # r - c
    anti_diagonal: set[int] = set()  # r + c
    placement: list[int] = []
    boards: list[list[str]] = []

    def explore(row: int) -> None:
        if row == n:
            boards.append(["." * c + "Q" + "." * (n - c - 1) for c in placement])
            return
        for col in range(n):
            if col in columns or (row - col) in diagonal or (row + col) in anti_diagonal:
                continue
            columns.add(col)
            diagonal.add(row - col)
            anti_diagonal.add(row + col)
            placement.append(col)

            explore(row + 1)

            placement.pop()
            anti_diagonal.discard(row + col)
            diagonal.discard(row - col)
            columns.discard(col)

    explore(0)
    return boards


CASES = [
    (([1, 2, 3],), [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]),
    (([0],), [[], [0]]),
    (([],), [[]]),
]


def solve(nums: list[int]) -> list[list[int]]:
    return subsets(nums)


def check() -> None:
    for args, expected in CASES:
        assert subsets(*args) == expected

    assert subsets_with_duplicates([1, 2, 2]) == [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]

    assert len(permutations([1, 2, 3])) == 6
    assert sorted(permutations([1, 2])) == [[1, 2], [2, 1]]
    assert permutations([]) == [[]]

    assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert combination_sum([2], 1) == []
    assert combination_sum([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]

    assert len(solve_n_queens(4)) == 2
    assert len(solve_n_queens(8)) == 92
    assert solve_n_queens(1) == [["Q"]]
    assert solve_n_queens(3) == []
