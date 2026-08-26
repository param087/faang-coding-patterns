"""Smallest Range Covering Elements from K Lists — LeetCode 632."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "insight": "Hold one pointer per list: the covering range is always [heap minimum, running maximum], and only advancing the minimum can shrink it.",
    "time": "O(n log k) over n total elements across k lists",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Given k **sorted** lists, find the smallest range `[a, b]` that contains at
least one element from every list. Ties break on the smaller `a`.

Confirm: the lists are sorted ascending (the whole solution rests on it),
values may be negative and may repeat, and a valid range always exists because
every list is non-empty. Ask what to return if a list *could* be empty —
nothing can cover it, so it is a contract question, not an algorithmic one.
""",
        ),
        (
            "The insight",
            """
Two framings get you there; use whichever the interviewer bites on.

**As a sliding window:** tag every value with its list index, merge all n values
into one sorted sequence, then run the "smallest window containing all k
labels" scan. Correct, O(n log n), and it is the same problem as Minimum Window
Substring.

**As a k-way merge**, which is tighter and what the heap is for: keep one
pointer per list. The k pointed-at values *already* cover every list, so the
candidate range is exactly `[min of the pointed values, max of them]`. Keep the
minimum in a heap and the maximum in a plain variable — it only ever grows,
because every advance pushes a pointer rightwards in a sorted list.

Now the key step: **the only move that can shrink the range is advancing the
list holding the minimum.** Advancing anything else leaves the lower bound
where it is and can only push the upper bound up. So pop the minimum, advance
that list, update the running max, record the range if it beat the best, and
repeat. `heapreplace` does the pop and push in one sift.

Stop as soon as **any list is exhausted**: past that point no range can cover
that list without reusing an element already passed, and its lower bound has
gone beyond the best you could still find.
""",
        ),
        (
            "Edge cases and the tie-break",
            """
- **Stop on the first exhausted list**, not when the heap empties. Draining the
  heap examines ranges that no longer cover all k lists and yields a wrong,
  too-small answer.
- **The tie-break falls out for free.** The popped minimum is non-decreasing
  across iterations, so with a strict `<` comparison the first range of a given
  width is also the one with the smallest `a`. Using `<=` would silently return
  a later range of equal width and fail the tie-break test.
- **k = 1** → `[first, first]`, width 0, and the loop returns on the first
  iteration if the list has one element. Check it: it is the cheapest
  correctness probe.
- **All lists identical** → width 0, e.g. `[[1,2,3],[1,2,3]]` → `[1,1]`.
- **Duplicates inside a list** are harmless; the heap entry carries `(value,
  list index, position)`, so equal values never collide.
- **The heap tuple must carry the list index and position**, not just the
  value, or you cannot advance the right pointer.
- **Compare widths, never store `b - a` alone.** Two ranges of equal width need
  their endpoints to apply the tie-break, and the answer is the pair anyway.
""",
        ),
    ],
}


def smallest_range(nums: list[list[int]]) -> list[int]:
    if not nums or any(not row for row in nums):
        return []  # an empty list cannot be covered — contract question

    heap = [(row[0], i, 0) for i, row in enumerate(nums)]  # (value, list, position)
    heapq.heapify(heap)
    current_max = max(row[0] for row in nums)
    best = [heap[0][0], current_max]

    while True:
        low, i, j = heap[0]
        if current_max - low < best[1] - best[0]:  # strict: keeps the smallest a
            best = [low, current_max]
        if j + 1 == len(nums[i]):  # this list is spent, so no range can cover it
            return best
        nxt = nums[i][j + 1]
        current_max = max(current_max, nxt)  # monotonically non-decreasing
        heapq.heapreplace(heap, (nxt, i, j + 1))


CASES = [
    (([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]],), [20, 24]),
    (([[1, 2, 3], [1, 2, 3], [1, 2, 3]],), [1, 1]),  # width 0, tie-break on a
    (([[1], [2], [3]],), [1, 3]),
    (([[10, 10], [11, 11]],), [10, 11]),  # duplicates within a list
    (([[-10, -9, -8], [-5, 0, 5], [4, 5, 6]],), [-8, 4]),  # negatives
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [3, 7]),  # disjoint ranges
    (([[1, 5, 9]],), [1, 1]),  # k = 1
    (([],), []),
]


def solve(nums: list[list[int]]) -> list[int]:
    return smallest_range([list(row) for row in nums])
