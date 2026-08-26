"""Maximum Sum Queries — LeetCode 2736."""

from __future__ import annotations

from bisect import bisect_left

META = {
    "pattern": "segment-tree",
    "insight": "Sort points and queries by the first constraint so the sweep satisfies it for free; the second constraint becomes a suffix-max query over compressed nums2.",
    "time": "O((n + q) log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Two arrays of the same length. For each query `[x, y]`, find the maximum of
`nums1[j] + nums2[j]` over indices `j` satisfying **both** `nums1[j] >= x` and
`nums2[j] >= y`; return −1 when no index qualifies.

`n` and `q` both reach 10⁵, so the double loop is 10¹⁰ index tests — hours. And
the two constraints are on *different* arrays while the objective is their sum,
which is what stops every one-dimensional shortcut.

Worth confirming: the comparisons are `>=`, not `>`, and the queries are
independent — nothing is consumed, so they may be answered in any order. That
second point is the licence to go offline, and it is the whole solution.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is to sort by `nums1` descending and keep a running
maximum of `nums1[j] + nums2[j]`. It ignores `y` entirely, so it returns the
biggest sum in the prefix even when that point's `nums2` is far too small:
`nums1 = [20, 4]`, `nums2 = [1, 9]`, query `[4, 5]` gives 21 where the answer is
13. Write that case down first; it kills the approach in one line.

The fix is to satisfy the two constraints by two different mechanisms.

**Constraint one, by sweep order.** Sort the points by `nums1` descending and
the queries by `x` descending, then walk the queries in that order, inserting
every point whose `nums1 >= x` before answering. Every point currently inserted
satisfies constraint one automatically — it never has to be checked again.

**Constraint two, by the tree.** Among the inserted points, the question is now
one-dimensional: maximum sum over those with `nums2 >= y`. Compress the `nums2`
values, index them **in reverse order** so that larger `nums2` gets a smaller
index, and "`nums2 >= y`" becomes a **prefix** of that ordering. A Fenwick tree
carrying `max` instead of `sum` answers prefix maxima in O(log n).

Total O((n + q) log n): each point inserted once, each query answered once.
""",
        ),
        (
            "The two details that decide it: reversal, and why max-Fenwick is legal",
            """
**A Fenwick tree does prefix aggregates, not suffix ones.** There is no
"subtract" for `max`, so you cannot compute a suffix max as total minus prefix.
Reversing the rank — `rank = len(ys) - bisect_left(ys, value)`, one-indexed —
turns the suffix you want into a prefix the structure can actually serve. If
`bisect_left` returns `len(ys)`, the rank is 0, the prefix is empty, and the
answer is −1: that is the "no qualifying `nums2`" case falling out for free
rather than needing a branch.

**A max-Fenwick is only valid because the updates never decrease a value.**
`tree[i] = max(tree[i], value)` on the way up is correct exactly when entries
are inserted and never removed or lowered — which is true here, since the sweep
only ever adds points. Say this: it is the reason a Fenwick is admissible at all
instead of a full segment tree, and it is the first thing that breaks if the
problem gains deletions.

Two smaller ones:

- Sweep on **`>=`, both sides**. The insert pointer condition and the query
  condition must both be `>=` or points tied exactly on `x` get dropped;
  `nums1 = [1,1,1]`, `nums2 = [5,5,5]`, query `[1,5]` catches it.
- Answers come back in **sorted-query order**; carry the original index and
  scatter them back, or the output is silently permuted. This is the single most
  common way an otherwise-correct offline solution fails.
""",
        ),
    ],
}


class MaxFenwick:
    """Prefix maximum. Valid only because values are inserted, never lowered."""

    def __init__(self, size: int) -> None:
        self.size = size
        self.tree = [-1] * (size + 1)  # -1 is the problem's "nothing qualifies"

    def insert(self, index: int, value: int) -> None:
        i = index + 1  # one-indexed: index 0 has no low bit
        while i <= self.size:
            if value > self.tree[i]:
                self.tree[i] = value
            i += i & -i

    def prefix_max(self, index: int) -> int:
        i = index + 1
        best = -1
        while i > 0:
            if self.tree[i] > best:
                best = self.tree[i]
            i -= i & -i
        return best


def maximum_sum_queries(
    nums1: list[int], nums2: list[int], queries: list[list[int]]
) -> list[int]:
    if not queries:
        return []

    ys = sorted(set(nums2))
    tree = MaxFenwick(len(ys))

    def reversed_rank(value: int) -> int:
        """Larger nums2 -> smaller rank, so `nums2 >= value` is a prefix."""
        return len(ys) - bisect_left(ys, value)

    points = sorted(zip(nums1, nums2, strict=True), reverse=True)  # by nums1 desc
    order = sorted(range(len(queries)), key=lambda i: -queries[i][0])

    answers = [-1] * len(queries)
    cursor = 0
    for query_index in order:
        x, y = queries[query_index]
        while cursor < len(points) and points[cursor][0] >= x:  # >=, not >
            a, b = points[cursor]
            tree.insert(reversed_rank(b) - 1, a + b)
            cursor += 1
        # rank 0 means no stored nums2 reaches y; prefix_max(-1) returns -1.
        answers[query_index] = tree.prefix_max(reversed_rank(y) - 1)
    return answers  # scattered back into the original query order


CASES = [
    (([4, 3, 1, 2], [2, 4, 9, 5], [[4, 1], [1, 3], [2, 5]]), [6, 10, 7]),
    (([3, 2, 5], [2, 3, 4], [[4, 4], [3, 2], [1, 1]]), [9, 9, 9]),
    (([2, 1], [2, 3], [[3, 3]]), [-1]),
    # The case that kills "running max of the sum, ignoring y": answer is 13.
    (([20, 4], [1, 9], [[4, 5]]), [13]),
    (([1], [1], [[1, 1], [2, 1], [1, 2]]), [2, -1, -1]),
    # Ties on both constraints must be admitted, not skipped.
    (([1, 1, 1], [5, 5, 5], [[1, 5]]), [6]),
    # Unsorted queries: the answers must come back in the original order.
    (([1, 5, 3], [3, 1, 4], [[1, 4], [5, 1], [3, 3], [6, 0]]), [7, 6, 7, -1]),
    (([], [], []), []),
]


def solve(
    nums1: list[int], nums2: list[int], queries: list[list[int]]
) -> list[int]:
    return maximum_sum_queries(
        list(nums1), list(nums2), [list(query) for query in queries]
    )
