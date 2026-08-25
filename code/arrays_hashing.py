"""Arrays and hashing templates.

The trade is always the same: spend O(n) memory to turn a nested scan into a
single pass. The interesting decision is *what to key on* — the value, a
canonical form of the value, or the running total so far.
"""

from __future__ import annotations

from collections import defaultdict


def two_sum(nums: list[int], target: int) -> list[int]:
    """Indices of the two values summing to target.

    The template. As you walk, ask "have I already seen the number that would
    complete this one?" — which turns a pair search into a membership test.
    Check *before* inserting, or a value pairs with itself.
    """
    seen: dict[int, int] = {}  # value -> index

    for i, value in enumerate(nums):
        want = target - value
        if want in seen:
            return [seen[want], i]
        seen[value] = i

    return []


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Group words that are anagrams of each other.

    Key on a *canonical form*: two words are anagrams exactly when their
    letter counts match. Sorting each word is O(k log k); the 26-length count
    tuple is O(k) and worth mentioning even if you write the sorted version.
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in words:
        counts = [0] * 26
        for char in word:
            counts[ord(char) - ord("a")] += 1
        groups[tuple(counts)].append(word)

    return list(groups.values())


def longest_consecutive(nums: list[int]) -> int:
    """Length of the longest run of consecutive integers, in O(n).

    The trick that makes it linear: only start counting from a value that has
    no left neighbour. Every run is then walked exactly once, so the inner
    while loop costs O(n) across the whole function rather than per element.
    """
    pool = set(nums)
    best = 0

    for value in pool:
        if value - 1 in pool:
            continue  # not the start of a run; someone else will count it
        length = 1
        while value + length in pool:
            length += 1
        best = max(best, length)

    return best


CASES = [
    (([2, 7, 11, 15], 9), [0, 1]),
    (([3, 2, 4], 6), [1, 2]),
    (([3, 3], 6), [0, 1]),
    (([], 0), []),
]


def solve(nums: list[int], target: int) -> list[int]:
    return two_sum(nums, target)


def check() -> None:
    for args, expected in CASES:
        assert two_sum(*args) == expected

    grouped = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert sorted(sorted(g) for g in grouped) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    assert group_anagrams([]) == []

    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longest_consecutive([]) == 0
    assert longest_consecutive([5]) == 1
