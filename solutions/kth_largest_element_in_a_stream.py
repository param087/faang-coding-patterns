"""Kth Largest Element in a Stream — LeetCode 703."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "symbol": "KthLargest",
    "insight": "Keep a min-heap holding exactly the k largest values seen; its root is the answer and anything smaller can be dropped on arrival.",
    "time": "O(n + (n - k) log n) to construct, O(log k) per add",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Build a class seeded with an array, then `add(val)` returns the **k-th largest
value in the stream so far**, counting duplicates as separate values.

Two clarifications worth voicing, because they change the code:

- **k-th largest, not k-th distinct largest.** `[5, 5]` with k = 2 answers 5.
  The distinct variant needs a set in front of the heap and is a different
  question.
- **How many `add` calls?** LeetCode says up to 10⁴, and the stream never ends
  in principle — which is the whole reason for keeping k things rather than n.
""",
        ),
        (
            "The insight",
            """
Sorting on every call is O(n log n) per `add`. Keeping the array sorted and
`bisect.insort`-ing is O(n) per call from the memmove. Both store the entire
stream to answer a question about **k** values.

Nothing below the k-th largest can ever become the k-th largest again — the
answer only moves up. So keep a **min-heap of size exactly k**: it holds the
top k seen so far, and its root *is* the k-th largest.

An arriving value is then one of two things:

- `val <= heap[0]` — it is not in the top k, so throw it away. O(1), and this
  is the common case on a long stream.
- `val > heap[0]` — it evicts the current root. `heapreplace` does the pop and
  the push in **one sift-down**, which is why it beats `heappush` followed by
  `heappop`.

Memory stays at O(k) no matter how long the stream runs. That is the answer
the question is fishing for; say it before writing the code.
""",
        ),
        (
            "Edge cases",
            """
- **The constructor can be handed fewer than k values.** LeetCode guarantees at
  least k − 1, so the very first `add` is the first call whose answer is
  defined. Guard with `if len(heap) < k: push` — without it you evict against a
  root that is not the k-th largest yet and the answer is permanently skewed.
- **k = 1** degenerates to a running maximum, and the heap is a one-element
  list. Worth checking out loud; it is the cheapest sanity test.
- **Duplicates count.** `KthLargest(2, [5, 5])` answers 5 on any `add(5)`.
  Anyone who reached for a set has answered a different problem.
- **Trimming the seed array.** `heapify` is O(n), then popping down to k is
  O((n − k) log n) — cheaper than pushing one at a time *and* cheaper than
  sorting when n is large relative to k.
- **Follow-up: k-th largest over a sliding window** rather than the whole
  stream. A heap cannot delete an arbitrary element, so that becomes lazy
  deletion or an ordered multiset — see Sliding Window Median.
""",
        ),
    ],
}


class KthLargest:
    """A min-heap holding exactly the k largest values seen so far."""

    def __init__(self, k: int, nums: list[int]) -> None:
        self.k = k
        self.heap = list(nums)  # copy: the caller's array is not ours to wreck
        heapq.heapify(self.heap)  # O(n), beats k pushes when n is large
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val: int) -> int:
        if len(self.heap) < self.k:  # seeded with fewer than k values
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:  # evicts the current k-th largest
            heapq.heapreplace(self.heap, val)  # one sift-down, not two
        return self.heap[0]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # The canonical sequence: 4 is displaced only once the stream grows.
    stream = KthLargest(3, [4, 5, 8, 2])
    assert stream.add(3) == 4
    assert stream.add(5) == 5
    assert stream.add(10) == 5
    assert stream.add(9) == 8
    assert stream.add(4) == 8
    assert len(stream.heap) == 3  # O(k) memory, not O(n)

    # Seeded with k - 1 values: the branch that a bare `heapreplace` gets wrong.
    short = KthLargest(2, [0])
    assert short.add(-1) == -1  # {0, -1} -> second largest is -1
    assert short.add(1) == 0
    assert short.add(-2) == 0  # rejected at the root, O(1)

    # k = 1 is a running maximum.
    running_max = KthLargest(1, [])
    assert running_max.add(-3) == -3
    assert running_max.add(-5) == -3
    assert running_max.add(7) == 7

    # Duplicates are distinct stream entries, not one value.
    duplicates = KthLargest(2, [5, 5])
    assert duplicates.add(5) == 5
    assert duplicates.add(4) == 5

    # Negatives only, and a seed longer than k.
    negatives = KthLargest(2, [-10, -4, -7, -1, -3])
    assert negatives.add(-8) == -3
    assert negatives.add(-2) == -2

    # A long stream of values below the threshold is rejected at the root and
    # never grows the heap.
    long_stream = KthLargest(3, [100, 200, 300])
    for value in range(-1000, 0):
        assert long_stream.add(value) == 100
    assert len(long_stream.heap) == 3
