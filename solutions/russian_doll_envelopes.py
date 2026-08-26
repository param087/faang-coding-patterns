"""Russian Doll Envelopes — LeetCode 354."""

from __future__ import annotations

from bisect import bisect_left

META = {
    "pattern": "dp-1d",
    "insight": "Sort by width ascending, height descending — the tie-break makes equal widths mutually exclusive, then it is plain LIS on heights.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Envelopes `(w, h)`. One nests inside another only if **both** dimensions are
strictly greater. Return the longest nesting chain.

Two clarifications that matter:

- **Strictly greater, or is equal allowed?** Strict. If equal were allowed the
  whole tie-break trick below evaporates and it becomes plain non-decreasing
  LIS on a plain sort.
- **Can envelopes be rotated?** No on LeetCode. If they could, you would
  normalise each pair to `(min, max)` first and the rest is unchanged — worth
  asking, because it is a one-line difference and it shows you read the
  constraints.

This is a **2-D LIS**. The sort kills one dimension; LIS handles the other.
n goes to 10⁵, so the O(n²) DP — 10¹⁰ comparisons — is not an option here even
though it is the honest starting point for LeetCode 300.
""",
        ),
        (
            "The insight",
            """
Sort by width ascending. Now any valid chain is a subsequence of the sorted
order, and the width condition is *almost* satisfied for free — almost, because
two envelopes of **equal width** appear one after the other and cannot nest.

Fix that in the comparator rather than in the loop: sort equal widths by height
**descending**. Within a width group the heights now strictly decrease, so no
increasing run can pick up two of them. Exactly one envelope per width can enter
any chain, which is precisely the rule.

With that ordering, run the O(n log n) patience-sorting LIS on the heights
alone: keep `tails`, where `tails[k]` is the smallest height that can end an
increasing run of length `k+1`, and `bisect_left` each height into it.

```python
sorted(envelopes, key=lambda e: (e[0], -e[1]))
```

That key is the entire difficulty of the problem. Everything after it is LeetCode
300 copied verbatim.
""",
        ),
        (
            "Why the tie-break, concretely",
            """
Take `[[1,3], [1,4], [1,5], [2,6]]`.

- Height **ascending** gives heights `3, 4, 5, 6` → LIS 4. Nonsense: three of
  those envelopes are all one unit wide and none nests in another.
- Height **descending** gives `(1,5), (1,4), (1,3), (2,6)` → heights `5, 4, 3, 6`
  → `tails` goes `[5] → [4] → [3] → [3, 6]` → **2**. Correct: one width-1
  envelope inside `(2,6)`.

Note that the three replacements at length 1 are not wasted work — they leave
the *smallest* width-1 height in `tails`, which is what makes room for `6`.

Two more traps worth naming:

- **`bisect_left`, not `bisect_right`.** Heights must be strictly increasing.
  `bisect_right` would let two envelopes of equal height chain, which the
  problem forbids.
- **`tails` is not a chain.** Only its length is meaningful; the heights in it
  may never have coexisted. Reconstructing the actual envelopes needs a parent
  array recorded during the scan.

Sorting is O(n log n) and the scan is O(n log n), so the sort is not the
bottleneck — it is the whole point.
""",
        ),
    ],
}


def max_envelopes(envelopes: list[list[int]]) -> int:
    if not envelopes:
        return 0

    # Width ascending; on ties, height DESCENDING so equal widths cannot chain.
    ordered = sorted(envelopes, key=lambda envelope: (envelope[0], -envelope[1]))

    tails: list[int] = []  # tails[k] = smallest height ending a chain of length k+1
    for _, height in ordered:
        position = bisect_left(tails, height)  # left => strictly increasing
        if position == len(tails):
            tails.append(height)
        else:
            tails[position] = height

    return len(tails)


CASES = [
    (([[5, 4], [6, 4], [6, 7], [2, 3]],), 3),
    (([[1, 3], [1, 4], [1, 5], [2, 6]],), 2),
    (([[1, 1], [1, 1], [1, 1]],), 1),
    (([[4, 5], [4, 6], [6, 7], [2, 3], [1, 1]],), 4),
    (([[30, 50], [12, 2], [3, 4], [12, 15]],), 3),
    (([[1, 1]],), 1),
    (([],), 0),
]


def solve(envelopes: list[list[int]]) -> int:
    return max_envelopes([list(envelope) for envelope in envelopes])
