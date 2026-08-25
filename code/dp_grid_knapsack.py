"""Grid DP and the knapsack family.

Two dimensions of state. Grid problems are the gentle introduction; knapsack
is the one worth really understanding, because the *direction of the inner loop*
encodes whether items may be reused, and that single detail is the difference
between the 0/1 and unbounded variants.
"""

from __future__ import annotations


def unique_paths(rows: int, cols: int) -> int:
    """Paths from top-left to bottom-right moving only right or down.

    `dp[c]` = ways to reach this column in the current row. Rolling one row at
    a time drops the space from O(rows·cols) to O(cols), and the update
    `dp[c] += dp[c-1]` reads as "from above, plus from the left" because
    `dp[c]` still holds the previous row when it is read.
    """
    dp = [1] * cols
    for _ in range(1, rows):
        for c in range(1, cols):
            dp[c] += dp[c - 1]
    return dp[-1]


def min_path_sum(grid: list[list[int]]) -> int:
    """Cheapest top-left to bottom-right path, moving right or down."""
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    dp = [float("inf")] * cols
    dp[0] = 0

    for r in range(rows):
        dp[0] += grid[r][0]
        for c in range(1, cols):
            dp[c] = min(dp[c], dp[c - 1]) + grid[r][c]

    return int(dp[-1])


def can_partition(nums: list[int]) -> bool:
    """Partition Equal Subset Sum — a 0/1 knapsack in disguise.

    "Split into two equal halves" is "can I hit exactly sum/2 using each
    element at most once". A set of reachable totals is enough; no counts
    needed.

    **The inner loop runs backwards.** Going forwards would let the same
    element be used twice within one pass, which is the unbounded knapsack.
    That direction is the entire 0/1-versus-unbounded distinction.
    """
    total = sum(nums)
    if total % 2:
        return False

    target = total // 2
    reachable = [False] * (target + 1)
    reachable[0] = True

    for value in nums:
        for amount in range(target, value - 1, -1):  # backwards: use once
            if reachable[amount - value]:
                reachable[amount] = True

    return reachable[target]


def coin_change_ways(coins: list[int], amount: int) -> int:
    """Number of *combinations* summing to amount — unbounded knapsack.

    The loop order matters here in a different way. Coins outside, amounts
    inside, counts each combination once. Swapping them counts *permutations*
    instead, turning "1+2" and "2+1" into two answers. That swap is the single
    most common bug in this problem.
    """
    dp = [0] * (amount + 1)
    dp[0] = 1

    for coin in coins:  # outer: combinations, not permutations
        for target in range(coin, amount + 1):  # forwards: reusable
            dp[target] += dp[target - coin]

    return dp[amount]


def maximal_square(matrix: list[list[str]]) -> int:
    """Area of the largest square of '1's.

    `dp[r][c]` = side of the largest square whose **bottom-right corner** is
    here. Fixing the corner is what makes the recurrence work: a square of
    side k needs three overlapping squares of side k-1 above, left, and
    diagonally, so the value is `1 + min` of those three.
    """
    if not matrix or not matrix[0]:
        return 0

    rows, cols = len(matrix), len(matrix[0])
    previous = [0] * (cols + 1)
    best = 0

    for r in range(rows):
        current = [0] * (cols + 1)
        for c in range(1, cols + 1):
            if matrix[r][c - 1] == "1":
                current[c] = 1 + min(previous[c], current[c - 1], previous[c - 1])
                best = max(best, current[c])
        previous = current

    return best * best


CASES = [
    ((3, 7), 28),
    ((3, 2), 3),
    ((1, 1), 1),
    ((7, 3), 28),
]


def solve(rows: int, cols: int) -> int:
    return unique_paths(rows, cols)


def check() -> None:
    for args, expected in CASES:
        assert unique_paths(*args) == expected

    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert min_path_sum([[1, 2, 3], [4, 5, 6]]) == 12
    assert min_path_sum([]) == 0

    assert can_partition([1, 5, 11, 5]) is True
    assert can_partition([1, 2, 3, 5]) is False
    assert can_partition([1, 1]) is True
    assert can_partition([1]) is False

    assert coin_change_ways([1, 2, 5], 5) == 4
    assert coin_change_ways([2], 3) == 0
    assert coin_change_ways([10], 10) == 1

    assert maximal_square(
        [
            ["1", "0", "1", "0", "0"],
            ["1", "0", "1", "1", "1"],
            ["1", "1", "1", "1", "1"],
            ["1", "0", "0", "1", "0"],
        ]
    ) == 4
    assert maximal_square([["0"]]) == 0
    assert maximal_square([["1"]]) == 1
