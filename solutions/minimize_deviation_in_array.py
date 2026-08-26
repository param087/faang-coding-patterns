"""Minimize Deviation in Array — LeetCode 1675."""

from __future__ import annotations

import heapq

META = {
    "pattern": "binary-search-answer",
    "insight": "Double every odd once and the two operations collapse into one: values can only be halved, so shrink the maximum and watch the spread.",
    "time": "O(n log n log(max value))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
You may double any **odd** element and halve any **even** element, each any
number of times. The deviation is `max - min` over the array. Minimise it.

Ask what the reachable set of a single element looks like — that question is
the answer. An odd `x` can go to `2x`, and from there halve back to `x`, so its
reachable set is `{x, 2x}` and nothing more (doubling twice gives `4x`, but
`4x` halves only back down to `x`). An even `x` reaches `x, x/2, x/4, …` down to
its odd core, and each of those can double back to where it came from. So every
element has a **finite chain** of at most `log(max)` values, and you are picking
one value per chain to minimise the spread.
""",
        ),
        (
            "The insight",
            """
**Normalise first: multiply every odd number by 2.** Now every value is even,
every chain is closed downwards, and the only remaining operation is halving.
That one line removes an entire direction of search and it is the step people
miss.

After that the greedy is forced. Take the current maximum: it is either the
unique thing keeping the deviation large, or it is not the maximum. Halving
anything else can only lower the minimum and never lowers the maximum, so the
*only* move that can improve the answer is halving the maximum. Do it, record
the new `max - min`, repeat. Stop when the maximum is odd — it cannot be halved,
and no further move can reduce the spread below the current one.

A max-heap gives the maximum in O(log n); the running minimum is a scalar,
since values only ever shrink. Each element is halved at most `log(max value)`
times, so the loop runs O(n log(max value)) times overall — about 10⁵ · 20 = 2 ×
10⁶ heap operations at the constraint limits.

Python has only a min-heap, so negate on the way in and out.
""",
        ),
        (
            "Why binary searching the deviation buys nothing",
            """
The chapter reflex is to guess the answer `d` and test feasibility, and it is
worth being able to say precisely why that is the wrong tool here.

`feasible(d)` would be "does some window `[L, L + d]` contain at least one value
from every element's chain?" It *is* monotone in `d`. The trouble is the check:
there is no cheap oracle for it. You would collect all `n log(max)` chain values
tagged with their owner, sort them, and slide a window that keeps every owner
covered — and the moment you have done that sweep you have the **exact minimum
window**, which is the answer itself. The binary search would then be an extra
`log` factor wrapped around a routine that already returned the result.

That reduction is worth naming anyway: this problem is **Smallest Range
Covering Elements from K Lists** (LC 632) with the lists generated rather than
given. The heap solution above is that sweep, specialised to chains that are
prefixes of one another so the window can be tracked with a single running
minimum instead of a pointer per list.

The general rule: binary searching the answer pays when the feasibility check
is *strictly easier* than the optimisation — a linear greedy, a reachability
test. When feasibility costs the same as optimality, drop the search.
""",
        ),
    ],
}


def minimum_deviation(nums: list[int]) -> int:
    # Normalise: after doubling the odds, every value can only ever be halved.
    heap = [-(value * 2 if value % 2 else value) for value in nums]
    heapq.heapify(heap)

    lowest = -max(heap)  # heap holds negatives, so max() is the smallest value
    best = -heap[0] - lowest

    while -heap[0] % 2 == 0:  # an odd maximum cannot shrink any further
        halved = -heapq.heappop(heap) // 2
        heapq.heappush(heap, -halved)
        lowest = min(lowest, halved)
        best = min(best, -heap[0] - lowest)

    return best


CASES = [
    (([1, 2, 3, 4],), 1),
    (([4, 1, 5, 20, 3],), 3),
    (([2, 10, 8],), 3),
    (([10, 4, 3],), 2),
    (([3, 5],), 1),
    (([2, 2, 2],), 0),
    (([1000000000, 1],), 1953123),
    (([1],), 0),
]


def solve(nums: list[int]) -> int:
    return minimum_deviation(list(nums))
