"""K Closest Points to Origin — LeetCode 973."""

from __future__ import annotations

import heapq
import random

META = {
    "pattern": "heaps",
    "symbol": "k_closest",
    "insight": "You need the k-th distance as a moving threshold, not a sorted array — a size-k max-heap keeps it, Quickselect finds it in O(n).",
    "time": "O(n log k) with the heap, O(n) expected with Quickselect",
    "space": "O(k) with the heap, O(1) extra with Quickselect",
    "sections": [
        (
            "What it asks",
            """
Given points on a plane and an integer k, return the k closest to the origin,
**in any order**.

Three clarifications that each change the answer:

- **Any order?** Yes — so nothing forces you to sort, which is the door to the
  O(n) solution.
- **Ties at the k-th distance?** Any k of them is accepted. If the interviewer
  says "deterministic tie-break", the heap key grows a second component and
  Quickselect needs care around equal keys.
- **Is n known up front, or is this a stream?** A stream rules out Quickselect
  entirely and makes the bounded heap the only answer.
""",
        ),
        (
            "Sorting, and when it is actually fine",
            """
`sorted(points, key=dist)[:k]` is one line and O(n log n). At n = 10⁴ (the
LeetCode bound) that is about 1.3·10⁵ comparisons — nothing. Say this, and say
you would ship it, before offering anything cleverer.

What makes it the wrong answer in an interview is the regime the question is
really about: **k ≪ n**. At n = 10⁸ points streaming through a mapper with
k = 100, sorting needs all 10⁸ resident (≈ 1.6 GB just for the tuples) and does
2.7·10⁹ comparisons; the heap holds 100 and does 10⁸ · log₂100 ≈ 6.6·10⁸.
Memory is the real difference, not the log factor.
""",
        ),
        (
            "The insight",
            """
The only thing you need at any moment is the **current k-th best distance** —
a threshold. Everything worse than it is dead, everything better evicts it.

A **max-heap capped at k** is exactly that structure: its root is the worst of
the k best so far, so an arriving point is either rejected in O(1) or swaps in
for O(log k). `heapq` is a min-heap, so the key is the **negated** distance.

Two details in the loop:

- Compare against `heap[0]` *before* pushing. `heappush` then `heappop` grows
  the heap to k + 1 and does two sift operations; `heapreplace` does one.
- Never take the square root. `√` is monotone, so `x² + y²` orders the points
  identically, stays in exact integer arithmetic, and dodges the float
  comparison that makes ties non-deterministic.
""",
        ),
        (
            "Quickselect, the O(n) answer",
            """
If the whole array is in memory, you can do better than O(n log k). Partition
around a pivot distance: after one pass the pivot sits at its final index p,
with everything closer to its left. If p = k − 1 you are done; otherwise
**recurse into one side only**.

Discarding half the work each time gives n + n/2 + n/4 + … = **2n** expected —
O(n). The catch is the pivot: on an adversarial or already-sorted input a
fixed pivot degenerates to O(n²), which at n = 10⁵ is 10¹⁰. Choosing the pivot
**at random** makes that outcome probabilistically impossible, and saying so
unprompted is the difference between "knows Quickselect" and "memorised it".

Cost: it mutates the input and needs the whole array — so it is strictly worse
than the heap for a stream, and strictly better for a batch.
""",
        ),
        (
            "The detail that decides it",
            """
The tuple pushed into the heap is `(-distance, x, y)`, and the ordering falls
through to `x` then `y` when distances tie. That is harmless here because
integers always compare.

It is **not** harmless in the version of this question that hands you objects:
`(-distance, point)` raises `TypeError: '<' not supported between instances of
'Point'` the first time two points tie, and ties are common (any point and its
reflection). The fix is a monotonically increasing counter as the second
element, so the comparison never reaches the payload:

```python
heapq.heappush(heap, (-distance, next(counter), point))
```

The same trap sinks task queues keyed on `(priority, task)`. Mention it — it
is a real production bug, not a puzzle.
""",
        ),
        (
            "Dry run",
            """
`points = [[3,3],[5,-1],[-2,4]]`, `k = 2`. Distances: 18, 26, 20.

- `[3,3]` → heap has room, push `(-18, 3, 3)`. Root worst = 18.
- `[5,-1]` → room, push `(-26, 5, -1)`. Root is now **−26**, the worst of two.
- `[-2,4]` → full. Is `(-20, -2, 4) > (-26, 5, -1)`? Yes, 20 < 26, so
  `heapreplace` evicts `[5,-1]`.

Heap holds `[3,3]` and `[-2,4]` — correct, and `[5,-1]` was never sorted
against anything. Note the root changed from 18 to 26 as the heap filled: the
threshold *loosens* while there is room and only tightens once at capacity.
That is the ordering bug people write when they check `val < heap[0]` before
the heap is full.
""",
        ),
        (
            "Follow-ups",
            """
- **"k closest to an arbitrary query point, many queries."** The heap is per
  query and O(n) each time. Build a **k-d tree** or a grid index once, then
  answer each query in O(log n + k) expected.
- **"The points do not fit in memory."** Bounded heap per shard, then merge the
  k shard-local heaps — top-k is decomposable, which is exactly why the heap
  version matters and the sort does not.
- **"Return them sorted by distance."** Pop the heap k times, or sort the k
  survivors: O(n log k + k log k), still not O(n log n).
- **Kth Largest Element in an Array (215)** is the same Quickselect with a
  scalar key; **Top K Frequent Elements (347)** is the same heap with a
  frequency key and a bucket-sort alternative.
""",
        ),
    ],
}


def k_closest(points: list[list[int]], k: int) -> list[list[int]]:
    """Bounded max-heap: O(n log k) time, O(k) space, works on a stream."""
    if k <= 0:
        return []  # otherwise the `elif` below indexes an empty heap
    heap: list[tuple[int, int, int]] = []  # (-distance, x, y), size <= k

    for x, y in points:
        candidate = (-(x * x + y * y), x, y)  # no sqrt: it is monotone
        if len(heap) < k:
            heapq.heappush(heap, candidate)
        elif candidate > heap[0]:  # closer than the current k-th best
            heapq.heapreplace(heap, candidate)  # one sift, not two

    return [[x, y] for _, x, y in heap]


def _distance(point: list[int]) -> int:
    return point[0] * point[0] + point[1] * point[1]


def _partition(points: list[list[int]], lo: int, hi: int) -> int:
    """Lomuto partition on a random pivot; returns the pivot's final index."""
    chosen = random.randint(lo, hi)  # random, or an adversary makes this O(n^2)
    points[chosen], points[hi] = points[hi], points[chosen]

    pivot = _distance(points[hi])
    store = lo
    for i in range(lo, hi):
        if _distance(points[i]) < pivot:
            points[store], points[i] = points[i], points[store]
            store += 1

    points[store], points[hi] = points[hi], points[store]
    return store


def k_closest_quickselect(points: list[list[int]], k: int) -> list[list[int]]:
    """O(n) expected, but needs the whole array and reorders it."""
    if k <= 0:
        return []
    scratch = [list(point) for point in points]  # never reorder the caller's list
    if k >= len(scratch):
        return scratch

    lo, hi = 0, len(scratch) - 1
    while lo < hi:
        pivot = _partition(scratch, lo, hi)
        if pivot == k - 1:
            break
        if pivot < k - 1:
            lo = pivot + 1  # recurse into one side only -> 2n total work
        else:
            hi = pivot - 1

    return scratch[:k]


CASES = [
    (([[1, 3], [-2, 2]], 1), [[-2, 2]]),
    (([[3, 3], [5, -1], [-2, 4]], 2), [[-2, 4], [3, 3]]),
    (([[0, 0]], 1), [[0, 0]]),  # the origin itself, distance 0
    (([[1, 1], [2, 2], [3, 3]], 3), [[1, 1], [2, 2], [3, 3]]),  # k == n
    (([[1, 0], [-1, 0], [0, 1], [0, -1]], 4), [[-1, 0], [0, -1], [0, 1], [1, 0]]),
    (([[-5, 4], [-6, -5], [4, 6]], 2), [[-5, 4], [4, 6]]),  # negatives, |d| 41 vs 61 vs 52
    (([[2, 2]], 0), []),  # k = 0
    (([[10000, 10000], [1, 1]], 1), [[1, 1]]),  # 2*10^8 stays exact as an int
]


def check() -> None:
    for index, (args, expected) in enumerate(CASES):
        points, k = args
        heap_answer = sorted(k_closest([list(p) for p in points], k))
        assert heap_answer == expected, f"heap case {index}: {heap_answer}"

        original = [list(point) for point in points]
        select_answer = sorted(k_closest_quickselect(points, k))
        assert select_answer == expected, f"quickselect case {index}: {select_answer}"

        # Quickselect partitions in place, so it must work on its own copy.
        assert points == original

    # Ties at the k-th distance: every point here is at distance 25, so any
    # two are a valid answer. Check the size and membership, not the identity.
    ring = [[3, 4], [4, 3], [-3, 4], [5, 0]]
    for answer in (k_closest(ring, 2), k_closest_quickselect(ring, 2)):
        assert len(answer) == 2
        assert all(point in ring for point in answer)

    # A sorted-by-distance input is the shape that makes a fixed pivot O(n^2).
    ordered = [[i, 0] for i in range(500)]
    assert sorted(k_closest_quickselect(ordered, 3)) == [[0, 0], [1, 0], [2, 0]]

    # The two implementations agree on random input, ties included.
    rng = random.Random(7)
    for _ in range(200):
        sample = [[rng.randint(-4, 4), rng.randint(-4, 4)] for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(sample))
        threshold = sorted(_distance(p) for p in sample)[k - 1]
        for answer in (k_closest(sample, k), k_closest_quickselect(sample, k)):
            assert len(answer) == k
            assert max(_distance(p) for p in answer) == threshold


def solve(points: list[list[int]], k: int) -> list[list[int]]:
    # Sorted so the cases are deterministic; the problem accepts any order.
    return sorted(k_closest([list(point) for point in points], k))
