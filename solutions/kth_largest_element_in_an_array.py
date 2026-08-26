"""Kth Largest Element in an Array — LeetCode 215."""

from __future__ import annotations

import heapq
import random

META = {
    "pattern": "divide-and-conquer",
    "symbol": "find_kth_largest",
    "insight": "Quickselect knows which half holds the answer and discards the other — T(n) = T(n/2) + n sums to O(n), not O(n log n).",
    "time": "O(n) expected, O(n²) worst case",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The k-th largest element by **position** in sorted order — so `[3,3,3]` with
k = 2 is 3, not "the second distinct value".

Ask: is k 1-indexed (yes); k-th largest by position or by distinctness (by
position — a real ambiguity worth confirming); may I mutate the input; is the
input a stream.
""",
        ),
        (
            "The ladder",
            """
Give all three. It reads far better than jumping to one:

1. **Sort**, take index `n - k`. O(n log n), one line, always correct.
2. **Min-heap of size k**. O(n log k). Better when k ≪ n, and the only option
   if the input is a stream.
3. **Quickselect**. O(n) expected, O(n²) worst case.

Then say which you would ship, and why. Having a reasoned preference is the
signal — not knowing the fastest one.
""",
        ),
        (
            "Why the heap is a MIN-heap",
            """
Counter-intuitive for about ten seconds. To keep the **largest** k you use a
**min**-heap, because its root is the weakest survivor — exactly the thing to
evict when a better candidate arrives.
""",
        ),
        (
            "The quickselect insight",
            """
Quicksort partitions and recurses into **both** halves: T(n) = 2T(n/2) + n,
which sums to O(n log n).

Quickselect knows which half contains the answer and **discards the other**:
T(n) = T(n/2) + n, which sums to **O(n)**.

Same partition, half the recursion, an entire complexity class better.
""",
        ),
        (
            "The random pivot is not optional",
            """
With a fixed pivot, sorted input degrades to O(n²) — and LeetCode's test cases
include sorted input precisely to catch that.

Say "I'll randomise the pivot to avoid the sorted-input worst case" as you
write it.

And be honest about the bound: O(n) **expected**, O(n²) worst. If they want a
guarantee, the answer is median-of-medians at O(n) worst case with a bad
constant — name it, do not attempt it.
""",
        ),
    ],
}


def find_kth_largest(nums: list[int], k: int) -> int:
    values = nums[:]  # don't mutate the caller's list
    target = len(values) - k  # k-th largest == this index once sorted ascending
    low, high = 0, len(values) - 1

    while low <= high:
        # Random pivot: a fixed one is O(n^2) on sorted input.
        pivot_index = random.randint(low, high)
        values[pivot_index], values[high] = values[high], values[pivot_index]
        pivot = values[high]

        store = low
        for i in range(low, high):
            if values[i] < pivot:
                values[store], values[i] = values[i], values[store]
                store += 1
        values[store], values[high] = values[high], values[store]

        if store == target:
            return values[store]
        if store < target:
            low = store + 1  # discard the left half entirely
        else:
            high = store - 1

    raise ValueError("k out of range")


def find_kth_largest_heap(nums: list[int], k: int) -> int:
    """The O(n log k) alternative — and the only one that works on a stream."""
    heap: list[int] = []
    for value in nums:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)  # evict the weakest survivor
    return heap[0]


CASES = [
    (([3, 2, 1, 5, 6, 4], 2), 5),
    (([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4),
    (([1], 1), 1),
    (([2, 1], 2), 1),
    (([3, 3, 3], 2), 3),
    (([7, 6, 5, 4, 3, 2, 1], 5), 3),
]


def solve(nums: list[int], k: int) -> int:
    return find_kth_largest(nums, k)


def check() -> None:
    for args, expected in CASES:
        assert find_kth_largest(*args) == expected
        assert find_kth_largest_heap(*args) == expected

    # Sorted input: the case a fixed pivot degrades on.
    ascending = list(range(200))
    assert find_kth_largest(ascending, 1) == 199
    assert find_kth_largest(ascending, 200) == 0
    assert find_kth_largest(ascending, 100) == 100
