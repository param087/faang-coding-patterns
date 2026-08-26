"""H-Index — LeetCode 274."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "The answer is capped by the paper count, so bucket citations at n and walk down — no sort and no search needed.",
    "time": "O(n)",
    "space": "O(n) for the buckets",
    "sections": [
        (
            "What it asks",
            """
Given each paper's citation count, return the largest `h` such that at least
`h` papers have at least `h` citations each.

The clarifying question that saves you: **is the input sorted?** If it is, this
is LeetCode 275 and the answer is a binary search in O(log n). If it is not —
this problem — the useful observation is that `h ≤ n`, which makes the input
values effectively bounded and opens the O(n) route.
""",
        ),
        (
            "The insight",
            """
`h` can never exceed `n`, the number of papers, so a citation count of 10 000
is indistinguishable from a count of `n` for the purpose of the answer. Clamp
every count into a bucket `min(citations, n)` — that is `n + 1` buckets total.

Now walk `h` down from `n`, accumulating how many papers have **at least** `h`
citations. The first `h` where that running total reaches `h` is the answer,
because the total only grows as `h` falls while the threshold only shrinks —
they cross exactly once.

The sort-based version (`sort descending`, return the largest `i` with
`citations[i] >= i + 1`) is fine at O(n log n) and worth mentioning as the
one-liner, but the clamp is the idea being tested.
""",
        ),
        (
            "Follow-ups",
            """
- **H-Index II** — the input arrives sorted ascending. Binary search on the
  index: `citations[mid] >= n - mid` means `n - mid` papers clear the bar, so
  move left. O(log n), and the off-by-one on `n - mid` is where it goes wrong.
- **Streaming citations** — keep the same `n + 1` bucket array, increment on
  arrival and re-walk only when the answer could have moved; each query is
  O(n) worst case but O(1) amortised if you track the running total.
- **Edge answers** — a single paper with 100 citations has h-index 1, not 100;
  a single paper with 0 citations has h-index 0. Both fall out of the walk
  without special-casing, which is a good sign the formulation is right.
""",
        ),
    ],
}


def h_index(citations: list[int]) -> int:
    n = len(citations)
    buckets = [0] * (n + 1)
    for count in citations:
        buckets[min(count, n)] += 1  # h can never exceed n, so clamp

    papers = 0  # papers with at least h citations
    for h in range(n, -1, -1):
        papers += buckets[h]
        if papers >= h:
            return h
    return 0


CASES = [
    (([3, 0, 6, 1, 5],), 3),
    (([1, 3, 1],), 1),
    (([0, 1, 2, 3, 4, 5, 6],), 3),
    (([4, 4, 4, 4],), 4),
    (([100],), 1),
    (([0, 0, 0],), 0),
    (([11, 15],), 2),
    (([],), 0),
]


def solve(citations: list[int]) -> int:
    return h_index(citations)
