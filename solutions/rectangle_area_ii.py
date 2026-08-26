"""Rectangle Area II — LeetCode 850."""

from __future__ import annotations

META = {
    "pattern": "segment-tree",
    "insight": "Sweep a vertical line across the rectangles; the only thing you need at each step is the total covered y-length, which a counting segment tree maintains without ever pushing lazily.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Total area covered by a set of axis-aligned rectangles, counting overlaps once,
modulo 10⁹ + 7.

The modulo is the tell: the true area can reach 10¹⁸, so the answer is not
something you can reach by inclusion–exclusion over subsets (2ⁿ terms at n = 200)
and not something that fits in 32 bits. Confirm the corner convention —
`[x1, y1, x2, y2]` is bottom-left and top-right, half-open in effect, so two
rectangles sharing an edge overlap in zero area.
""",
        ),
        (
            "The insight",
            """
Sweep a vertical line left to right. Between two consecutive x-coordinates
nothing enters or leaves, so the covered region is a constant set of y-intervals
and the area contributed by that slab is

```
covered_y_length * (x_next - x_current)
```

Every rectangle becomes two events: `+1` on its y-interval at `x1`, `-1` at
`x2`. So the whole problem reduces to a data structure that maintains a
multiset of y-intervals under add/remove and reports **the total length covered
at least once**.

Compress the y-coordinates the same way as in Falling Squares: leaf `j` is the
half-open gap `[ys[j], ys[j+1])`, so "share an edge" cannot become "share a
leaf". With at most 2n gaps the tree is tiny; 2n events, each O(log n), gives
O(n log n) against the O(n²·log n) of the coordinate-grid scan.
""",
        ),
        (
            "The trick that makes this tree unusual: no lazy propagation",
            """
This looks like a range-update problem, so people reach for lazy propagation and
then discover the tag will not compose. It does not need one. Each node keeps
two numbers:

- `count` — how many rectangle intervals cover **this node exactly**, i.e. the
  add/remove deltas that stopped their descent here;
- `covered` — the covered length within the node's span.

and `covered` is recomputed bottom-up by one rule:

```
covered = full span      if count > 0
        = 0              if count == 0 and this is a leaf
        = left.covered + right.covered   otherwise
```

The reason it works — and this is the sentence to say out loud — is that
**counts are only ever removed by the same node that added them**, because every
`-1` event decomposes into exactly the same set of nodes as its `+1` did. So a
`count` is never stale and never needs pushing down. A node with `count > 0` is
fully covered regardless of its children, which is why the children's values can
sit there untouched and wrong.

Two pitfalls around the edges:

- **Do not take the modulo until the end.** The covered length is a geometric
  quantity; reducing it mod 10⁹+7 and multiplying by a width produces garbage.
  In Python accumulate exactly and reduce once; the `[[0,0,10⁹,10⁹]]` case
  returns **49**, which is the standard check that you did this right.
- **Degenerate rectangles** with `x1 == x2` or `y1 == y2` contribute nothing but
  will hand the tree an empty leaf range (`hi < lo`) if you let them through.
  Filter them at event-build time.
""",
        ),
    ],
}

MOD = 10**9 + 7


class CoveredLengthTree:
    """Add/remove y-intervals, report total covered length. No lazy tags needed."""

    def __init__(self, ys: list[int]) -> None:
        self.ys = ys
        self.size = max(len(ys) - 1, 1)  # leaves are the gaps between coordinates
        self.count = [0] * (4 * self.size)
        self.covered = [0] * (4 * self.size)

    def update(self, left: int, right: int, delta: int,
               node: int = 1, lo: int = 0, hi: int | None = None) -> None:
        hi = self.size - 1 if hi is None else hi
        if right < lo or hi < left:
            return
        if left <= lo and hi <= right:
            self.count[node] += delta  # the -1 lands on exactly these nodes
        else:
            mid = (lo + hi) // 2
            self.update(left, right, delta, 2 * node, lo, mid)
            self.update(left, right, delta, 2 * node + 1, mid + 1, hi)

        if self.count[node] > 0:
            self.covered[node] = self.ys[hi + 1] - self.ys[lo]
        elif lo == hi:
            self.covered[node] = 0
        else:
            self.covered[node] = self.covered[2 * node] + self.covered[2 * node + 1]

    @property
    def total(self) -> int:
        return self.covered[1]


def rectangle_area(rectangles: list[list[int]]) -> int:
    ys = sorted({y for x1, y1, x2, y2 in rectangles for y in (y1, y2)})
    if len(ys) < 2:
        return 0

    index = {y: i for i, y in enumerate(ys)}
    events: list[tuple[int, int, int, int]] = []
    for x1, y1, x2, y2 in rectangles:
        if x1 == x2 or y1 == y2:  # degenerate: no area, and an empty leaf range
            continue
        events.append((x1, 1, index[y1], index[y2] - 1))
        events.append((x2, -1, index[y1], index[y2] - 1))
    if not events:
        return 0
    events.sort()

    tree = CoveredLengthTree(ys)
    area = 0
    previous_x = events[0][0]
    for x, delta, lo, hi in events:
        area += tree.total * (x - previous_x)  # exact, no modulo yet
        previous_x = x
        tree.update(lo, hi, delta)
    return area % MOD


CASES = [
    (([[0, 0, 2, 2], [1, 0, 2, 3], [1, 0, 3, 1]],), 6),
    # 10^18 mod (10^9 + 7) = 49 — the check that you deferred the modulo.
    (([[0, 0, 1000000000, 1000000000]],), 49),
    (([],), 0),
    (([[0, 0, 1, 1]],), 1),
    # Exact duplicates must be counted once.
    (([[0, 0, 2, 2], [0, 0, 2, 2]],), 4),
    (([[0, 0, 1, 1], [2, 2, 3, 3]],), 2),
    # Sharing an edge is zero overlap: gaps-as-leaves, not points-as-leaves.
    (([[0, 0, 1, 1], [1, 0, 2, 1]],), 2),
    # Negative coordinates, one rectangle strictly inside another.
    (([[-3, -3, 3, 3], [-1, -1, 1, 1]],), 36),
]


def solve(rectangles: list[list[int]]) -> int:
    return rectangle_area([list(rectangle) for rectangle in rectangles])
