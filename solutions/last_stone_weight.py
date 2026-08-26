"""Last Stone Weight — LeetCode 1046."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "insight": "Only the two heaviest stones ever matter, and the debris rejoins the same queue — that is a max-heap, not a sort.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Repeatedly smash the two heaviest stones together: equal weights destroy both,
otherwise the difference goes back into the pile. Return the last remaining
weight, or 0 if none remains.

Ask what to return for an **empty input** — LeetCode guarantees at least one
stone, so 0 is a defensive choice, not a specified one. Say which you picked.
""",
        ),
        (
            "The insight",
            """
Sorting is the wrong shape. Each smash **inserts a new value** whose position
in the order is unknown, so a sorted array pays O(n) per re-insert and you do
up to n − 1 smashes: O(n²), and at n = 3·10⁴ that is 9·10⁸ shifts for a problem
that should take microseconds.

You never need the pile ordered, only its **two largest elements**, and a heap
gives those in O(log n) while absorbing the new stone at the same cost.

`heapq` is min-only, so negate on the way in and negate on the way out. Say
"negating for a max-heap" out loud — silently sign-flipped values are the main
source of confusion when reading this back. `heapify` on the negated list is
O(n); the log factor comes from the smashes, not the build.

The pushed value is `second - first`, which is already ≤ 0 and is exactly the
negation of `first - second`. Writing `-(first - second)` is the same number
and one more chance to drop a sign.
""",
        ),
        (
            "Edge cases",
            """
- **Equal weights push nothing.** `[2, 2]` empties the heap, so the return must
  handle an empty heap, not just `-heap[0]`. That is the branch a solution
  written for the sample input misses.
- **Odd counts can still cancel.** `[1, 1, 1]` smashes two to nothing and
  leaves 1; `[10, 10, 9, 8]` cancels the pair, then leaves 9 − 8 = 1. Parity of
  the count tells you nothing.
- **A single stone** is already the answer, and the `while len(heap) > 1` guard
  handles it without a special case.
- **All weights are positive** (1 ≤ w ≤ 1000), which is what makes 0 an
  unambiguous "nothing left" sentinel. If zero-weight stones were allowed you
  would need a count instead.
- **Follow-up: n = 10⁷ with weights bounded by 1000.** Counting sort the
  weights into a 1001-bucket array and walk it downwards — O(n + W), no heap.
  The bound in the constraints is there for a reason.
""",
        ),
    ],
}


def last_stone_weight(stones: list[int]) -> int:
    heap = [-weight for weight in stones]  # negated: heapq is min-only
    heapq.heapify(heap)  # O(n), not n pushes

    while len(heap) > 1:
        first = -heapq.heappop(heap)  # heaviest
        second = -heapq.heappop(heap)  # second heaviest
        if first != second:
            heapq.heappush(heap, second - first)  # already negative

    return -heap[0] if heap else 0  # equal weights can empty the heap


CASES = [
    (([2, 7, 4, 1, 8, 1],), 1),
    (([1],), 1),
    (([],), 0),
    (([2, 2],), 0),  # the heap empties — the branch samples do not cover
    (([1, 1, 1],), 1),
    (([10, 10, 9, 8],), 1),  # odd survivor from an even-sized pile
    (([3, 7, 2],), 2),
    (([1000, 1000, 1000],), 1000),
]


def solve(stones: list[int]) -> int:
    return last_stone_weight(stones)
