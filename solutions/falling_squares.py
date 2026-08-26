"""Falling Squares — LeetCode 699."""

from __future__ import annotations

META = {
    "pattern": "segment-tree",
    "insight": "Each square is a range-max read followed by a range-assign write, so the structure needed is a max segment tree with lazy assignment over compressed x.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Squares drop one at a time onto a number line. Square `i` is given as
`[left, side]` and lands on the interval `[left, left + side)`; it comes to rest
on top of the tallest thing already under any part of that interval. After each
drop, report the tallest stack anywhere on the line.

Two clarifying questions decide the implementation:

- **Is the interval half-open?** Yes. Two squares that meet at a single x do not
  stack. `[[100, 100], [200, 100]]` is `[100, 100]`, not `[100, 200]`.
- **Is the output the height of *this* square or the running maximum?** The
  running maximum — so the answer list is non-decreasing, and a square that
  lands low still reports the old high-water mark.

Also worth asking: `left` and `side` go up to 10⁸, so the line is far too wide
to index directly. Only the 2n endpoints matter.
""",
        ),
        (
            "Brute force, and the number that decides whether it survives",
            """
Keep a list of landed squares as `(left, right, height)`. For each new square,
scan the whole list for x-overlap, take the max height, add `side`. O(n²).

At LeetCode's `n ≤ 1000` that is 10⁶ comparisons and it **passes** — say so,
write it if you are short on time, and do not pretend otherwise. But the
interview follow-up is always the same: the same problem with n = 10⁵ drops is
10¹⁰ comparisons, roughly three hours. That is the version worth solving.
""",
        ),
        (
            "The insight",
            """
Strip the geometry and each drop is exactly two range operations on x:

1. **read** the maximum height over `[left, left + side)`;
2. **write** that maximum plus `side` to every point in `[left, left + side)` —
   an *assignment* over the range, not an increment.

Range-max query plus range-assign update is precisely a segment tree with lazy
propagation, so this is one of the few problems where the structure is not a
clever choice but a direct translation of the statement. O(log n) each, O(n log n)
overall.

The x-axis is compressed first: collect all 2n endpoints (`left` **and**
`left + side`), sort the distinct values, and let leaf `j` of the tree represent
the **gap** `[xs[j], xs[j+1])`. There are at most 2n − 1 gaps, height inside a
gap is constant, and every square's footprint is an exact contiguous run of
gaps — which is what makes the compression lossless.
""",
        ),
        (
            "The detail that decides it: gaps, not points",
            """
Compressing to points and letting leaf `j` mean "the coordinate `xs[j]`" is the
standard way this goes wrong. Under that mapping a square covering `[100, 200)`
and one covering `[200, 300)` both touch the leaf for 200, and the second one
climbs on top of the first. The answer comes back 200 instead of 100.

Mapping leaves to the **half-open gaps between** consecutive coordinates fixes
it structurally: `[left, left + side)` becomes the leaf range
`index[left] .. index[left + side] - 1`, so a square that ends where another
begins shares no leaf at all. No special-casing anywhere else in the code.

Two more that bite:

- The lazy tag is **assign**, not add. Pushing down must *overwrite* the child's
  value and tag. Getting this wrong shows up only when one square lands on a
  region that two earlier squares split, so small tests miss it.
- Query before you assign, on the same interval. Reversing the order makes every
  square land on itself.
""",
        ),
        (
            "Dry run",
            """
`[[1, 2], [2, 3], [6, 1]]`

Endpoints `{1, 3, 2, 5, 6, 7}` → `xs = [1, 2, 3, 5, 6, 7]`, so five gaps:
`[1,2) [2,3) [3,5) [5,6) [6,7)`.

- `[1, 2]` covers `[1, 3)` = gaps 0–1. Max there is 0, so it lands at **2**.
  Assign 2 to gaps 0–1. Best = 2.
- `[2, 3]` covers `[2, 5)` = gaps 1–2. Gap 1 is already at 2, gap 2 at 0, so the
  max is 2 and it lands at **5**. Assign 5 to gaps 1–2. Best = 5. Note gap 0 is
  untouched and stays at 2 — the partial overlap is why an assign has to be a
  *range* assign and not a whole-interval reset.
- `[6, 1]` covers `[6, 7)` = gap 4. Max 0, lands at **1**. Best stays **5**.

Answer `[2, 5, 5]`. The third entry is the one that catches anyone returning the
new square's own height.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it without a segment tree."** Coordinate-compressed brute force over
  the gap array — a plain list of 2n heights, scanned and overwritten per drop —
  is O(n²) but with a tiny constant and about six lines. Good fallback.
- **"Report the height of each square rather than the running max."** Drop the
  `best` accumulator; the tree work is identical. Worth confirming which one is
  wanted before you start.
- **Skyline / My Calendar III** are the same lazy machinery with `+1` instead of
  assign, and `The Skyline Problem` swaps the sweep for a multiset.
- **"Squares can be removed."** Assignment is not invertible, so the lazy tag
  breaks; you need the full history per interval, i.e. a segment tree of
  multisets or offline processing in reverse.
""",
        ),
    ],
}


class MaxAssignTree:
    """Range-max query with range-assign update, over `size` leaves."""

    def __init__(self, size: int) -> None:
        self.size = max(size, 1)
        self.tree = [0] * (4 * self.size)
        self.lazy: list[int | None] = [None] * (4 * self.size)  # pending assignment

    def _apply(self, node: int, value: int) -> None:
        self.tree[node] = value  # assign, not add
        self.lazy[node] = value

    def _push(self, node: int) -> None:
        pending = self.lazy[node]
        if pending is not None:
            self._apply(2 * node, pending)
            self._apply(2 * node + 1, pending)
            self.lazy[node] = None

    def assign(self, left: int, right: int, value: int, node: int = 1,
               lo: int = 0, hi: int | None = None) -> None:
        hi = self.size - 1 if hi is None else hi
        if right < lo or hi < left:
            return
        if left <= lo and hi <= right:
            self._apply(node, value)
            return
        self._push(node)
        mid = (lo + hi) // 2
        self.assign(left, right, value, 2 * node, lo, mid)
        self.assign(left, right, value, 2 * node + 1, mid + 1, hi)
        self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])

    def query(self, left: int, right: int, node: int = 1,
              lo: int = 0, hi: int | None = None) -> int:
        hi = self.size - 1 if hi is None else hi
        if right < lo or hi < left:
            return 0
        if left <= lo and hi <= right:
            return self.tree[node]
        self._push(node)
        mid = (lo + hi) // 2
        return max(
            self.query(left, right, 2 * node, lo, mid),
            self.query(left, right, 2 * node + 1, mid + 1, hi),
        )


def falling_squares(positions: list[list[int]]) -> list[int]:
    if not positions:
        return []

    # Compress x, then let leaf j be the half-open gap [xs[j], xs[j + 1]).
    xs = sorted({x for left, side in positions for x in (left, left + side)})
    index = {x: i for i, x in enumerate(xs)}
    tree = MaxAssignTree(len(xs) - 1)

    heights: list[int] = []
    best = 0
    for left, side in positions:
        lo, hi = index[left], index[left + side] - 1  # gap range, so hi is exclusive-1
        landed = tree.query(lo, hi) + side  # read first...
        tree.assign(lo, hi, landed)  # ...then write
        best = max(best, landed)
        heights.append(best)
    return heights


CASES = [
    (([[1, 2], [2, 3], [6, 1]],), [2, 5, 5]),
    # Touching at a single x must NOT stack — this is the half-open test.
    (([[100, 100], [200, 100]],), [100, 100]),
    (([[1, 5], [2, 2]],), [5, 7]),
    (([],), []),
    (([[1, 1]],), [1]),
    # A square landing low still reports the running maximum.
    (([[4, 6], [1, 1]],), [6, 6]),
    # Partial overlaps stacking three deep, with a stale-high-water check.
    (([[2, 4], [3, 3], [9, 4], [7, 7], [4, 7]],), [4, 7, 7, 11, 18]),
    (([[9, 7], [1, 9], [3, 1]],), [7, 16, 17]),
]


def solve(positions: list[list[int]]) -> list[int]:
    return falling_squares([list(square) for square in positions])
