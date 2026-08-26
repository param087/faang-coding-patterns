"""Range Module — LeetCode 715."""

from __future__ import annotations

from bisect import bisect_left, bisect_right

META = {
    "pattern": "intervals",
    "symbol": "RangeModule",
    "insight": "Keep one canonical list of disjoint half-open ranges and every operation is two binary searches plus one slice assignment.",
    "time": "O(log n) to locate plus O(n) for the splice per add/remove; O(log n) per query",
    "space": "O(n) — one entry per surviving range",
    "sections": [
        (
            "What it asks",
            """
Track a set of numbers as ranges. `addRange(left, right)` marks
**`[left, right)`** as tracked, `removeRange` unmarks it, and
`queryRange(left, right)` returns whether **every** number in `[left, right)`
is currently tracked.

The intervals are **half-open** — `right` is excluded — and that is stated in
the problem rather than left to you, so restate it back: `[1,3)` and `[3,5)`
are disjoint but together cover `[1,5)`. Also worth confirming: coordinates
are up to 10⁹, so nothing can be indexed by value; and `queryRange` is
all-or-nothing, not "does any of it overlap".
""",
        ),
        (
            "The insight",
            """
Store the tracked set in exactly one canonical form: a list of ranges that is
sorted, disjoint, and **never touching** — after `[1,3)` and `[3,5)` are
added, the list holds `[[1,5]]` and nothing else. Every operation then
restores that form by construction instead of by case analysis:

- **add** — binary search the window of stored ranges that touch or overlap
  `[left, right)`, widen the bounds to include the outermost of them, and
  replace the whole window with that one range;
- **remove** — binary search the window that *strictly* overlaps, and replace
  it with the at most **two** surviving fragments: the head of the first range
  and the tail of the last;
- **query** — find the single range that could contain `left` (the last one
  starting at or before it) and check that it reaches `right`. Nothing else
  can help: a gap anywhere inside means false.

Both mutators end in `ranges[i:j] = replacement`, a slice assignment that
deletes and inserts in one step. That is what keeps the invariant airtight —
there is no intermediate state where the list is not canonical.
""",
        ),
        (
            "The comparisons that decide it",
            """
This is Hard because of four boundary conditions, not because of the
structure. Fix which side is inclusive before writing a single `bisect`:

- **add** takes `end >= left` and `start <= right` — **non-strict**, because
  touching ranges must merge: adding `[3,5)` next to `[1,3)` has to yield
  `[1,5)`, not two entries;
- **remove** takes `end > left` and `start < right` — **strict**, because
  touching ranges must *not* be disturbed: removing `[3,5)` must leave `[1,3)`
  completely intact.

Get those two the same way round and the structure silently degrades — either
the list accumulates adjacent fragments that make later queries fail, or a
remove eats a range it never touched.

Then the two fragments in `remove`: `ranges[i][0] < left` produces a head, and
`ranges[j-1][1] > right` produces a tail. When the window is a single range
strictly containing the removal, **both** fire — removing `[14,16)` from
`[10,20)` leaves `[10,14)` and `[16,20)`. A version that returns after the
first fragment passes the obvious tests and loses the tail.

At 10⁴ calls the O(n) splice is comfortably fast. The asymptotically clean
answer is a segment tree with lazy propagation over coordinate-compressed
endpoints, O(log n) per operation — name it, then write this, because a
lazy-propagation segment tree is not a 35-minute artefact.
""",
        ),
    ],
}


class RangeModule:
    def __init__(self) -> None:
        # Sorted, disjoint, non-touching, half-open [start, end).
        self._ranges: list[list[int]] = []

    def add_range(self, left: int, right: int) -> None:
        ranges = self._ranges
        # Non-strict on both sides: a merely touching range must merge in.
        i = bisect_left(ranges, left, key=lambda r: r[1])  # first end >= left
        j = bisect_right(ranges, right, key=lambda r: r[0])  # first start > right

        if i < j:  # the window is non-empty: widen to swallow it
            left = min(left, ranges[i][0])
            right = max(right, ranges[j - 1][1])

        ranges[i:j] = [[left, right]]

    def query_range(self, left: int, right: int) -> bool:
        ranges = self._ranges
        i = bisect_right(ranges, left, key=lambda r: r[0]) - 1  # last start <= left
        return i >= 0 and ranges[i][1] >= right

    def remove_range(self, left: int, right: int) -> None:
        ranges = self._ranges
        # Strict on both sides: a merely touching range must be left alone.
        i = bisect_right(ranges, left, key=lambda r: r[1])  # first end > left
        j = bisect_left(ranges, right, key=lambda r: r[0])  # first start >= right

        survivors = []
        if i < j:
            if ranges[i][0] < left:
                survivors.append([ranges[i][0], left])  # head of the first
            if ranges[j - 1][1] > right:
                survivors.append([right, ranges[j - 1][1]])  # tail of the last

        ranges[i:j] = survivors


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    module = RangeModule()
    assert module.query_range(1, 2) is False  # empty structure

    module.add_range(10, 20)
    module.remove_range(14, 16)
    assert module.query_range(10, 14) is True
    assert module.query_range(13, 15) is False  # spans the hole
    assert module.query_range(16, 17) is True
    # Both fragments survived the interior removal.
    assert module._ranges == [[10, 14], [16, 20]]

    # Half-open: touching adds merge, touching removes do not disturb.
    touching = RangeModule()
    touching.add_range(1, 3)
    touching.add_range(3, 5)
    assert touching._ranges == [[1, 5]]
    assert touching.query_range(1, 5) is True
    touching.remove_range(5, 9)
    assert touching._ranges == [[1, 5]]
    touching.remove_range(3, 5)
    assert touching._ranges == [[1, 3]]
    assert touching.query_range(1, 3) is True
    assert touching.query_range(1, 4) is False

    # A single add bridging several stored ranges collapses them all.
    bridging = RangeModule()
    for start in range(0, 100, 10):
        bridging.add_range(start, start + 5)
    assert len(bridging._ranges) == 10
    bridging.add_range(2, 97)
    assert bridging._ranges == [[0, 97]]
    assert bridging.query_range(0, 97) is True
    assert bridging.query_range(96, 98) is False

    # A remove spanning several ranges keeps only the outer fragments.
    spanning = RangeModule()
    for start in (1, 10, 20, 30):
        spanning.add_range(start, start + 5)
    spanning.remove_range(3, 32)
    assert spanning._ranges == [[1, 3], [32, 35]]

    # Idempotence: re-adding a covered sub-range changes nothing.
    idempotent = RangeModule()
    idempotent.add_range(5, 50)
    idempotent.add_range(10, 20)
    assert idempotent._ranges == [[5, 50]]
    # Removing a prefix then a suffix leaves the middle.
    idempotent.remove_range(0, 10)
    idempotent.remove_range(40, 90)
    assert idempotent._ranges == [[10, 40]]
    assert idempotent.query_range(10, 40) is True
    assert idempotent.query_range(9, 40) is False

    # Removing everything empties the structure rather than leaving [x, x).
    emptied = RangeModule()
    emptied.add_range(1, 4)
    emptied.remove_range(1, 4)
    assert emptied._ranges == []
    assert emptied.query_range(1, 2) is False
    # Large coordinates: nothing may be indexed by value.
    emptied.add_range(1, 10**9)
    assert emptied.query_range(999_999_998, 10**9) is True
