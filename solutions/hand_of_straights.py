"""Hand of Straights — LeetCode 846."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "greedy",
    "insight": "The smallest card left has no smaller partner, so it must start a group — that forces the entire group and removes all choice.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Partition a multiset of integers into groups of exactly `groupSize`
**consecutive** values. Return whether it is possible.

Identical to *Divide Array in Sets of K Consecutive Numbers* (LeetCode 1296) —
same code, and worth saying so if it comes up.

First check, before any logic: `len(hand) % groupSize` must be 0, or the
answer is `False` for free.
""",
        ),
        (
            "The insight",
            """
There is no search here. Look at the **smallest remaining card**, `m`. Nothing
smaller exists, so no group can contain `m` in any position except the first —
which forces that group to be exactly `m, m+1, ..., m+groupSize-1`. If any of
those values is missing, the answer is `False` immediately; there is no
alternative arrangement to back-track into.

The same argument applies to every duplicate of `m` at once: if `m` appears `k`
times, then `k` groups all start at `m`, so you consume `k` copies of each of
the next `groupSize - 1` values in one step. That batching is what keeps the
loop linear in the number of *distinct* values rather than in `n`.

So: count, walk the distinct values in sorted order, and for each one with a
positive remaining count, subtract that count from the whole window ahead.
""",
        ),
        (
            "Pitfalls",
            """
- **Decrementing one card at a time** turns the loop into O(n · groupSize) and,
  worse, tempts you into a `while` over the raw sorted list where duplicates
  are re-examined. Batch by count.
- **Missing values read as zero.** `Counter[x]` returns 0 for an absent key
  without inserting it, so the `<` test works — but a plain `dict[x]` raises
  and a `defaultdict` silently grows while you iterate. Snapshot the key order
  (`sorted(counts)`) before the loop either way.
- **Skipping exhausted values.** After batching, a value's count can be 0; it
  must be skipped, not treated as the start of a zero-sized group.
- `groupSize == 1` is always `True`, and `groupSize == len(hand)` means the
  hand must be one unbroken run.
- The heap variant ("pop the min, extend the run") is the same algorithm with
  worse constants. The counting version is easier to defend.
""",
        ),
    ],
}


def is_n_straight_hand(hand: list[int], group_size: int) -> bool:
    if group_size <= 0 or len(hand) % group_size:
        return False

    counts = Counter(hand)

    for card in sorted(counts):  # snapshot: no keys are added below
        need = counts[card]
        if need <= 0:
            continue
        # `card` must open `need` groups, so the whole window is forced.
        for offset in range(group_size):
            if counts[card + offset] < need:
                return False
            counts[card + offset] -= need

    return True


CASES = [
    (([1, 2, 3, 6, 2, 3, 4, 7, 8], 3), True),
    (([1, 2, 3, 4, 5], 4), False),  # length not divisible by groupSize
    (([1, 2, 3, 4, 5, 6], 2), True),
    (([1, 1, 2, 2, 3, 3], 3), True),  # duplicates open two groups at once
    (([1, 1, 2, 2, 3, 4], 3), False),  # the second 1 has no 3 to finish on
    (([8, 10, 12], 3), False),  # sorted but not consecutive
    (([5, 5, 5], 1), True),  # groups of one always work
    (([], 3), True),
]


def solve(hand: list[int], group_size: int) -> bool:
    return is_n_straight_hand(hand, group_size)
