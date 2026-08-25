"""Randomized algorithms and sampling.

Small category, disproportionately common at Google and Meta, and one where
the interviewer usually wants a **proof of uniformity** rather than just
working code. Have the induction ready.
"""

from __future__ import annotations

from bisect import bisect_left


class WeightedPicker:
    """Random Pick with Weight — sample index i with probability w[i]/sum(w).

    Prefix sums turn weights into contiguous ranges on a number line; a
    uniform draw into that line lands in a range with exactly the right
    probability, and binary search finds which. O(log n) per pick after an
    O(n) build.

    `bisect_left` against the *inclusive* prefix totals is the correct bound.
    `bisect_right` shifts every pick by one and silently gives weight to the
    wrong index.
    """

    def __init__(self, weights: list[int]) -> None:
        self.prefix: list[int] = []
        running = 0
        for weight in weights:
            running += weight
            self.prefix.append(running)
        self.total = running

    def pick(self, draw: float) -> int:
        """`draw` in [0, 1) is injected so the tests are deterministic."""
        target = draw * self.total
        return bisect_left(self.prefix, target + 1e-12)


def reservoir_sample(stream: list[int], k: int, randoms: list[float]) -> list[int]:
    """Uniformly sample k items from a stream of unknown length, O(k) space.

    The i-th item (0-based) is kept with probability k/(i+1), replacing a
    uniformly chosen survivor. The induction: assume every earlier item is
    held with probability k/i; a new item enters with k/(i+1), and an
    incumbent survives with `1 - (k/(i+1))·(1/k)` — multiply through and you
    get k/(i+1) again.

    `randoms` is injected so the test can pin the outcome.
    """
    reservoir: list[int] = []

    for i, value in enumerate(stream):
        if i < k:
            reservoir.append(value)
            continue
        # Keep with probability k/(i+1).
        position = int(randoms[i - k] * (i + 1))
        if position < k:
            reservoir[position] = value

    return reservoir


def shuffle(nums: list[int], randoms: list[float]) -> list[int]:
    """Fisher-Yates, the only correct in-place shuffle.

    Swap position i with a uniformly random position in `[i, n)`. The common
    wrong version draws from `[0, n)` — it produces n^n equally likely
    swap sequences over n! permutations, and since n^n is not divisible by
    n!, some orderings are strictly more likely. That is the trap the
    question exists to test.
    """
    values = nums[:]
    for i in range(len(values)):
        j = i + int(randoms[i] * (len(values) - i))  # from [i, n), not [0, n)
        values[i], values[j] = values[j], values[i]
    return values


class LinkedListSampler:
    """Pick a random node from a list of unknown length — reservoir with k=1.

    The single-item case, worth naming separately because the phrasing hides
    it: "you don't know the length and can't store the list" *is* reservoir
    sampling.
    """

    def __init__(self, values: list[int]) -> None:
        self.values = values

    def get_random(self, randoms: list[float]) -> int:
        chosen = self.values[0]
        for i, value in enumerate(self.values[1:], start=1):
            if randoms[i - 1] < 1 / (i + 1):
                chosen = value
        return chosen


CASES = [
    (([1], [0.0]), 0),
    (([1, 3], [0.0]), 0),
    (([1, 3], [0.5]), 1),
    (([1, 3], [0.99]), 1),
]


def solve(weights: list[int], draws: list[float]) -> int:
    return WeightedPicker(weights).pick(draws[0])


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    picker = WeightedPicker([1, 3])
    # Weight 1 owns [0, 1); weight 3 owns [1, 4).
    assert picker.pick(0.0) == 0
    assert picker.pick(0.2) == 0
    assert picker.pick(0.3) == 1
    assert picker.pick(0.99) == 1

    # Every draw >= k lands outside the reservoir, so the first k survive.
    assert reservoir_sample([1, 2, 3, 4, 5], 2, [0.99, 0.99, 0.99]) == [1, 2]
    # A draw of 0 always replaces slot 0.
    assert reservoir_sample([1, 2, 3], 2, [0.0]) == [3, 2]
    assert reservoir_sample([1, 2], 5, []) == [1, 2]

    # Identity randoms: each i picks j == i, so nothing moves.
    assert shuffle([1, 2, 3], [0.0, 0.0, 0.0]) == [1, 2, 3]
    assert sorted(shuffle([1, 2, 3], [0.9, 0.9, 0.0])) == [1, 2, 3]

    sampler = LinkedListSampler([1, 2, 3])
    assert sampler.get_random([0.9, 0.9]) == 1  # never replaces
    assert sampler.get_random([0.0, 0.0]) == 3  # always replaces
