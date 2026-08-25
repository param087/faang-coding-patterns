"""1-D dynamic programming.

Three questions, in order, and the first is the one people skip:

1. **What is the state?** What does `dp[i]` mean, in a sentence?
2. **What is the recurrence?** How does `dp[i]` follow from earlier entries?
3. **What are the base cases?**

If you cannot say (1) in a sentence, do not write code yet. Most failed DP
attempts are state failures, not coding failures.
"""

from __future__ import annotations


def climb_stairs(n: int) -> int:
    """Ways to climb n steps taking 1 or 2 at a time.

    `dp[i]` = number of ways to reach step i. You arrive from i-1 or i-2, so
    `dp[i] = dp[i-1] + dp[i-2]` — Fibonacci wearing a hat. Only the last two
    values are ever read, so the table folds to two variables.
    """
    if n <= 2:
        return max(n, 1)

    previous, current = 1, 2
    for _ in range(3, n + 1):
        previous, current = current, previous + current
    return current


def rob(nums: list[int]) -> int:
    """House Robber: max sum with no two adjacent elements.

    `dp[i]` = best takeable from the first i houses. At each house, either skip
    it (`dp[i-1]`) or take it and add `dp[i-2]`. The decision-per-element shape
    is the most common 1-D DP there is.
    """
    take, skip = 0, 0
    for value in nums:
        take, skip = skip + value, max(skip, take)
    return max(take, skip)


def coin_change(coins: list[int], amount: int) -> int:
    """Fewest coins summing to amount, or -1.

    `dp[a]` = fewest coins for amount a. Unbounded: each coin may be reused,
    which is why the inner loop runs forward over amounts rather than
    backward. Compare with the 0/1 knapsack, where the direction flips.
    """
    unreachable = amount + 1
    dp = [unreachable] * (amount + 1)
    dp[0] = 0

    for target in range(1, amount + 1):
        for coin in coins:
            if coin <= target:
                dp[target] = min(dp[target], dp[target - coin] + 1)

    return -1 if dp[amount] == unreachable else dp[amount]


def length_of_lis(nums: list[int]) -> int:
    """Longest strictly increasing subsequence, in O(n log n).

    The O(n²) DP is `dp[i]` = best LIS ending at i. This is the patience-sorting
    version: `tails[k]` holds the smallest possible tail of an increasing
    subsequence of length k+1. `tails` is sorted, so binary search places each
    value.

    `tails` is **not** a valid subsequence — only its length is meaningful.
    Interviewers ask; do not claim otherwise.
    """
    from bisect import bisect_left

    tails: list[int] = []
    for value in nums:
        position = bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value  # a smaller tail is strictly better
    return len(tails)


def word_break(s: str, word_dict: list[str]) -> bool:
    """Can s be segmented into dictionary words?

    `dp[i]` = "the first i characters can be segmented". For each position,
    look back for a split point that was reachable and leaves a valid word.
    O(n²·L). The `trie` tag LeetCode puts on this is an alternative approach,
    not the canonical one.
    """
    words = set(word_dict)
    dp = [False] * (len(s) + 1)
    dp[0] = True  # the empty prefix is trivially segmentable

    for end in range(1, len(s) + 1):
        for start in range(end):
            if dp[start] and s[start:end] in words:
                dp[end] = True
                break

    return dp[len(s)]


CASES = [
    (([1, 2, 3, 1],), 4),
    (([2, 7, 9, 3, 1],), 12),
    (([2, 1, 1, 2],), 4),
    (([5],), 5),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return rob(nums)


def check() -> None:
    for args, expected in CASES:
        assert rob(*args) == expected

    assert climb_stairs(2) == 2
    assert climb_stairs(3) == 3
    assert climb_stairs(1) == 1
    assert climb_stairs(45) == 1836311903

    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1
    assert coin_change([1], 0) == 0

    assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert length_of_lis([0, 1, 0, 3, 2, 3]) == 4
    assert length_of_lis([7, 7, 7, 7]) == 1
    assert length_of_lis([]) == 0

    assert word_break("leetcode", ["leet", "code"]) is True
    assert word_break("applepenapple", ["apple", "pen"]) is True
    assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
