"""Shuffle an Array — LeetCode 384."""

from __future__ import annotations

import random
from collections import Counter

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Fisher-Yates draws the partner for slot i from [i, n) — restricting the range is exactly what makes all n! orderings equally likely.",
    "time": "O(n) per shuffle, O(1) per reset amortised",
    "space": "O(n) to hold the original",
    "sections": [
        (
            "What it asks",
            """
Wrap an array in `reset()` (hand back the original order) and `shuffle()`
(hand back a uniformly random permutation). **Uniform** means all n!
orderings are equally likely — not merely that the output looks jumbled.

Two things worth pinning down before writing anything. `reset()` must be
*exact*, so keep a defensive copy of the input rather than shuffling in place
and hoping. And when they say random, they are grading the distribution: this
question exists so you will name the bias in the naive swap.
""",
        ),
        (
            "The insight",
            """
Fisher-Yates, one pass, in place.

At position `i`, pick `j` uniformly from `[i, n)` and swap. Slot `i` is then
finalised and never touched again — the unshuffled suffix shrinks by one each
step.

The counting argument is the answer to *why is it uniform*: the first slot has
n candidates, the second n−1, the third n−2, so the algorithm has exactly n!
equally likely execution paths and each one produces a different permutation.
A bijection onto the n! outcomes, so every outcome has probability 1/n!.

O(n) time, O(1) extra space beyond the stored original, one RNG call per
element.
""",
        ),
        (
            "The one-character bug, and the test that finds it",
            """
Draw `j` from `[0, n)` instead of `[i, n)` — the "swap every element with a
random other element" version — and the output still looks perfectly jumbled.
It is measurably biased.

That variant has nⁿ equally likely paths mapping onto n! permutations, and nⁿ
is not divisible by n! for n > 2, so by pigeonhole some permutations *must*
come out more often than others. Concretely, for
n = 3: 27 paths over 6 permutations, and the identity turns up 4/27 = **14.8%**
of the time instead of 16.7%.

You cannot see a 2-point bias by eye, which is the real lesson — randomised
code needs a histogram test, not an eyeball test. The `check()` below draws
60,000 shuffles of a 3-element array and asserts each of the six orderings
lands within 5% of 10,000. The buggy version fails it by a mile (8,889 for the
identity); this one passes.
""",
        ),
    ],
}


class Solution:
    def __init__(self, nums: list[int]) -> None:
        self.original = list(nums)  # defensive copy — reset() must be exact
        self.current = list(nums)

    def reset(self) -> list[int]:
        self.current = list(self.original)
        return self.current

    def shuffle(self) -> list[int]:
        array = self.current
        for i in range(len(array) - 1):  # the last slot has only itself left
            j = random.randrange(i, len(array))  # at or after i — never before
            array[i], array[j] = array[j], array[i]
        return array


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # Degenerate sizes must not raise: range(-1) and range(0) are both empty.
    assert Solution([]).shuffle() == []
    assert Solution([7]).shuffle() == [7]
    assert Solution([]).reset() == []

    # The multiset is preserved, duplicates and negatives included.
    source = [-3, 0, 0, 5, 5, 5, 9]
    keeper = Solution(source)
    for _ in range(200):
        assert sorted(keeper.shuffle()) == sorted(source)
    assert keeper.reset() == source
    assert source == [-3, 0, 0, 5, 5, 5, 9], "the caller's list must not be touched"

    # reset() after a shuffle restores the exact original, repeatedly.
    for _ in range(10):
        keeper.shuffle()
        assert keeper.reset() == source

    # Uniformity: all 3! orderings within 5% of even. A [0, n) swap range
    # gives the identity 4/27 = 8,889 of these draws and fails here.
    draws = 60_000
    picker = Solution([1, 2, 3])
    seen = Counter(tuple(picker.shuffle()) for _ in range(draws))
    assert len(seen) == 6, f"expected all 6 permutations, saw {sorted(seen)}"
    for ordering, count in seen.items():
        assert abs(count - draws / 6) < 500, f"{ordering} came up {count} times"

    # Every element must be able to reach every position.
    positions: list[set[int]] = [set() for _ in range(4)]
    spreader = Solution([10, 20, 30, 40])
    for _ in range(400):
        for index, value in enumerate(spreader.shuffle()):
            positions[index].add(value)
    assert all(slot == {10, 20, 30, 40} for slot in positions)
