"""Minimum Cost to Connect Sticks — LeetCode 1167."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "insight": "Every stick pays once for each merge above it, so the shortest sticks must sit deepest — merge the two smallest and put the result back.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

You have sticks of given lengths. Connecting two sticks costs the sum of their
lengths and leaves one stick of that combined length. Keep going until a single
stick remains and return the **minimum total cost**.

Worth confirming: you may connect any two sticks, not just adjacent ones (yes —
that is what separates this from the O(n³) matrix-chain-shaped variant), and a
pile of one stick costs 0.

This is Huffman coding with the letters spelled differently. Saying that out
loud early is worth more than the code.
""",
        ),
        (
            "The insight",
            """
Write down what the total cost actually is. A stick of length L that ends up
`d` merges deep in the merge tree is added into the running total exactly `d`
times, so

```
total = Σ length_i × depth_i
```

which is precisely the weighted path length Huffman minimises. Long sticks must
sit shallow, short sticks deep — so at every step you merge the **two shortest
remaining** sticks, and the new combined stick competes for future merges on
equal terms.

That last clause is the whole algorithm. The combined stick must go **back into
the queue**, because it may well no longer be among the smallest. A min-heap
gives both operations in O(log n), so the loop is O(n log n) overall, dominated
by the n − 1 merges rather than the O(n) `heapify`.
""",
        ),
        (
            "The fold that looks identical, and is not",
            """
The tempting shortcut is to sort once and fold left to right:
`((s₀ + s₁) + s₂) + …`, no heap needed. It gives the right answer often enough
to pass a hand-check and then quietly loses money.

`[1, 2, 3, 4, 5]`:

- **Left fold:** 1+2 = 3, then 3+3 = 6, then 6+4 = 10, then 10+5 = 15 →
  total **34**.
- **Heap:** 1+2 = 3 (total 3); the heap is now `[3, 3, 4, 5]`, so the next
  merge is 3+3 = 6 (total 9); then 4+5 = 9 (total 18); then 6+9 = 15 →
  total **33**.

The fold forces a left-leaning tree; the heap lets 4 and 5 pair with each other
instead of being dragged along by the accumulator. `[1, 1, 1, 1]` shows the
same gap: 9 for the fold, 8 for the heap.

Two other things to watch:

- **n ≤ 1 returns 0**, not the stick's length. The `while len(heap) > 1` guard
  covers it, but state it — "one stick costs nothing" is a real edge case here.
- **The result of a merge is pushed, so values grow.** With n = 10⁴ sticks of
  10⁴ the total reaches ~10⁹; in a fixed-width language that is a 64-bit
  accumulator. Python does not care, but say it.
""",
        ),
    ],
}


def connect_sticks(sticks: list[int]) -> int:
    heap = list(sticks)  # copy — heapify reorders in place
    heapq.heapify(heap)  # O(n)

    total = 0
    while len(heap) > 1:
        merged = heapq.heappop(heap) + heapq.heappop(heap)
        total += merged
        heapq.heappush(heap, merged)  # it competes for the next merge too

    return total


CASES = [
    (([2, 4, 3],), 14),
    (([1, 8, 3, 5],), 30),
    (([1, 2, 3, 4, 5],), 33),  # the left fold says 34
    (([1, 1, 1, 1],), 8),  # the left fold says 9
    (([5],), 0),  # one stick is already connected
    (([],), 0),
    (([1, 1],), 2),
    (([10000, 1, 1, 10000],), 30006),  # 2 + 10002 + 20002
]


def solve(sticks: list[int]) -> int:
    return connect_sticks(sticks)
