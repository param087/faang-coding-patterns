"""Find K Pairs with Smallest Sums — LeetCode 373."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "insight": "The sums form a matrix sorted along both axes, so a heap holding one cell per row walks the frontier without building n·m pairs.",
    "time": "O(k log k)",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Two **sorted** arrays. Take one element from each to form a pair; return the k
pairs with the smallest sums.

The word "sorted" is the entire question — say it back to the interviewer. Also
confirm: k can exceed `len(nums1) × len(nums2)` (return everything), pairs are
by position so duplicate values give duplicate pairs, and any order is fine
among ties at the k-th sum.
""",
        ),
        (
            "The insight",
            """
Building all pairs and sorting is O(n·m log(n·m)). With both arrays at 10⁵
that is 10¹⁰ pairs — you run out of memory long before time.

Picture the sums as a matrix `M[i][j] = nums1[i] + nums2[j]`. Because both
inputs are sorted, **every row and every column is non-decreasing**. That makes
it the k-way-merge shape: each row is a sorted list, and the smallest unused
sum is always at the head of some row.

So seed a min-heap with the head of each row — `(nums1[i] + nums2[0], i, 0)` —
and pop k times, each pop pushing its row's next cell `(i, j + 1)`. Every pop
is the global minimum of the frontier, so the pops come out in sum order.

Two economies matter:

- **Seed only `min(k, len(nums1))` rows.** Row i's *smallest* sum already uses
  `nums2[0]`, so if k rows are ahead of it, nothing in row i can reach the top
  k. Seeding all 10⁵ rows for k = 3 is the difference between O(k log k) and
  O(n log n).
- **Never push a cell twice.** Expanding only rightwards from a popped cell
  (never downwards) means each cell has exactly one parent, so no `visited`
  set is needed. The variant that expands both ways *does* need one.
""",
        ),
        (
            "Edge cases",
            """
- **Either array empty, or k ≤ 0** → `[]`. The heap comprehension would
  otherwise index `nums2[0]` and raise `IndexError`.
- **k greater than n·m.** The loop is `while heap and len(out) < k`, so it
  stops when the frontier empties rather than trying to pop from nothing.
- **Duplicate values.** `nums1 = [1, 1]` legitimately yields `[1, 1]` twice
  from different rows; deduplicating by *value* is wrong.
- **Negative values** change nothing — sortedness is all the algorithm uses.
- **Ties at the k-th sum** make the answer non-unique: with `[1,1,2]` and
  `[1,2,3]`, sums 3 appear from `(1,2)` and `(2,1)`. Any k of them is accepted,
  so verify by *sum*, not by identity, when you write your own tests.
- **The heap tuple ordering** falls through to `i` and `j` on equal sums, which
  is harmless for ints; with objects in the payload it raises `TypeError`, and
  the fix is a tiebreak counter in the tuple.
""",
        ),
    ],
}


def k_smallest_pairs(nums1: list[int], nums2: list[int], k: int) -> list[list[int]]:
    if not nums1 or not nums2 or k <= 0:
        return []

    # One frontier entry per row, and only the rows that can reach the top k.
    heap = [(nums1[i] + nums2[0], i, 0) for i in range(min(k, len(nums1)))]
    heapq.heapify(heap)

    pairs: list[list[int]] = []
    while heap and len(pairs) < k:
        _, i, j = heapq.heappop(heap)
        pairs.append([nums1[i], nums2[j]])
        if j + 1 < len(nums2):  # advance this row only — one parent per cell
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))

    return pairs


CASES = [
    (([1, 7, 11], [2, 4, 6], 3), [[1, 2], [1, 4], [1, 6]]),
    (([1, 1, 2], [1, 2, 3], 2), [[1, 1], [1, 1]]),  # duplicate values, distinct pairs
    (([1, 2], [3], 3), [[1, 3], [2, 3]]),  # k exceeds n*m
    (([], [1, 2], 3), []),
    (([1, 2], [1, 2], 0), []),
    (([-10, -4, 0, 0, 6], [3, 5, 6, 7, 8, 100], 1), [[-10, 3]]),
    (([1], [1], 1), [[1, 1]]),
    # 10^6 pairs exist; only three rows are ever seeded.
    ((list(range(1000)), list(range(1000)), 3), [[0, 0], [0, 1], [1, 0]]),
]


def solve(nums1: list[int], nums2: list[int], k: int) -> list[list[int]]:
    # Sorted so the cases are deterministic; the problem accepts any order.
    return sorted(k_smallest_pairs(nums1, nums2, k))
