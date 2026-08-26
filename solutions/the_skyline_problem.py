"""The Skyline Problem — LeetCode 218."""

from __future__ import annotations

import heapq

META = {
    "pattern": "intervals",
    "insight": "Sweep the 2n critical x-values holding a max-heap of live heights, and emit a point only when the roof actually changes.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Buildings are `[left, right, height]` rectangles on the ground line. Return the
outline of their union as key points `[x, height]` — one per place where the
roof changes level, sorted by x, ending at height 0, with **no two consecutive
points at the same height**.

Ask three things:

- Are the buildings sorted by `left`? (On LeetCode yes, but the sweep sorts its
  own events anyway, so do not build the answer on that.)
- Are the right edges **exclusive**? Effectively yes — a building occupies
  `[left, right)`, which is why one ending exactly where another begins must
  not produce a drop to 0.
- How large are the coordinates? Up to 2³¹, which kills any sweep over integer
  positions before you write it.
""",
        ),
        (
            "Brute force, and why it fails",
            """
The outline can only change at a left or right edge, so there are at most `2n`
interesting x-values. For each one, scan every building and take the maximum
height covering it.

With n = 10⁴ buildings that is 2·10⁴ × 10⁴ = **2·10⁸** operations — an order of
magnitude too slow in Python and marginal even in C++.

The worse version, sweeping every integer x, is not slow but impossible:
coordinates reach 2³¹, so that is 2 billion columns. Say this out loud; it is
the reason the answer has to be event-driven rather than position-driven.
""",
        ),
        (
            "The insight",
            """
Sweep left to right over the critical x-values, holding the set of buildings
that are **currently live**. The roof at any x is the maximum height in that
set, so the answer is: at each event, update the set, look at the maximum, and
emit `[x, max]` only if it differs from the last emitted height.

A max-heap gives the maximum in O(1). The problem is the *removal*: when a
building ends, it has to leave the heap, and `heapq` has no "delete this
element". Solving that is the real content of the question — everything else is
bookkeeping.
""",
        ),
        (
            "Lazy deletion, and the event encoding",
            """
**Lazy deletion.** Do not remove a building when it ends. Push
`(-height, right)` and, at each new x, pop from the top while
`heap[0][1] <= x` — a root whose right edge has passed is dead and cannot be
the roof. Anything expired but buried deeper is harmless: it is not the maximum
now, and it will be discarded before it ever becomes the maximum. Each building
is pushed once and popped at most once, so the whole sweep stays **O(n log n)**
even though the inner `while` looks quadratic.

**The event encoding is where this problem is won or lost.** Starts are
`(x, -height, right)`, ends are `(x, 0, 0)`, and plain tuple sorting then gives
exactly the order needed:

- At a shared x, **starts come before ends** (`-height < 0`). Without that, a
  building ending where a taller one begins pops the roof to 0 and emits a
  spurious point, then immediately emits another — a classic wrong answer that
  passes the first sample.
- Among starts at the same x, the **tallest goes first**, so only one point is
  emitted rather than a staircase of increasing heights.
- Among ends at the same x, order does not matter; they are all `(x, 0, 0)`.

**The sentinel.** Seed the heap with `(0, inf)` so it is never empty and the
ground level is always available — otherwise every gap between buildings needs
a special case.

**The dedupe.** Emitting only when the height differs from the previous point
is what enforces "no two consecutive points at the same height". It also
silently handles nested buildings, buildings of equal height sharing an edge,
and duplicate rectangles.
""",
        ),
        (
            "Dry run",
            """
`[[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]`

| x | event | heap top | emit |
|---|-------|----------|------|
| 2 | start 10 | 10 | `[2,10]` |
| 3 | start 15 | 15 | `[3,15]` |
| 5 | start 12 | 15 | — (no change) |
| 7 | end of 15 | 12 | `[7,12]` |
| 9 | end of 10 | 12 | — (12 was already on top) |
| 12 | end of 12 | 0 | `[12,0]` |
| 15 | start 10 | 10 | `[15,10]` |
| 19 | start 8 | 10 | — |
| 20 | end of 10 | 8 | `[20,8]` |
| 24 | end of 8 | 0 | `[24,0]` |

The rows that emit nothing are the point: the heap changes far more often than
the skyline does.

Then run `[[1,2,1],[2,3,1]]` → `[[1,1],[3,0]]`. Two equal-height buildings
sharing an edge form **one** rectangle, and this is the case that catches both
a bad event order and a missing dedupe.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it without a heap."** Divide and conquer: the skyline of one building
  is trivial, and two skylines merge like merge sort — walk both by x, keep the
  last height seen on each side, and emit `max` when it changes. Also
  O(n log n), and it is the natural answer in a language with no priority
  queue. Implemented below as `get_skyline_divide`, and the tests assert the
  two agree.
- **"Why not delete from the heap properly?"** In C++ you can —
  `std::multiset` gives O(log n) erase and the code shortens. In Python, lazy
  deletion is the idiom; know that the distinction exists.
- **Streaming buildings** — the sweep needs all events up front, so a
  [balanced BST or ordered multiset](../../patterns/ordered-set/) replaces the
  heap.
- **Rectangle Area II** (union of rectangle *areas*) is the same sweep with
  a segment tree measuring covered length instead of a heap tracking a maximum.
""",
        ),
    ],
}


def get_skyline(buildings: list[list[int]]) -> list[list[int]]:
    # Starts sort before ends at a shared x because -height < 0, and taller
    # starts sort before shorter ones. That ordering is the whole trick.
    events: list[tuple[int, int, int]] = [
        (left, -height, right) for left, right, height in buildings
    ]
    events += [(right, 0, 0) for _, right, _ in buildings]
    events.sort()

    live: list[tuple[int, float]] = [(0, float("inf"))]  # (-height, right); ground sentinel
    result: list[list[int]] = [[0, 0]]  # sentinel, dropped on return

    for x, negative_height, right in events:
        while live[0][1] <= x:  # lazy deletion: the top has expired
            heapq.heappop(live)
        if negative_height:  # a start event
            heapq.heappush(live, (negative_height, right))

        height = -live[0][0]
        if result[-1][1] != height:  # emit only when the roof actually changes
            result.append([x, height])

    return result[1:]


def get_skyline_divide(buildings: list[list[int]]) -> list[list[int]]:
    """Divide and conquer — same O(n log n), no priority queue."""
    if not buildings:
        return []
    if len(buildings) == 1:
        left, right, height = buildings[0]
        return [[left, height], [right, 0]]

    middle = len(buildings) // 2
    return _merge_skylines(
        get_skyline_divide(buildings[:middle]),
        get_skyline_divide(buildings[middle:]),
    )


def _merge_skylines(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    i = j = 0
    left_height = right_height = 0

    while i < len(left) and j < len(right):
        if left[i][0] < right[j][0]:
            x, left_height = left[i]
            i += 1
        elif right[j][0] < left[i][0]:
            x, right_height = right[j]
            j += 1
        else:  # same x: both sides change here
            x, left_height = left[i]
            right_height = right[j][1]
            i += 1
            j += 1

        height = max(left_height, right_height)
        if not merged or merged[-1][1] != height:
            merged.append([x, height])

    # Whichever list is exhausted has fallen to height 0, so the tail passes
    # through untouched — apart from the same dedupe.
    for point in left[i:] + right[j:]:
        if merged and merged[-1][1] == point[1]:
            continue
        merged.append(point[:])

    return merged


CASES = [
    (
        ([[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]],),
        [[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]],
    ),
    (([[1, 2, 1], [2, 3, 1]],), [[1, 1], [3, 0]]),
    (([[1, 10, 5], [2, 4, 5]],), [[1, 5], [10, 0]]),
    (([[1, 5, 10], [5, 9, 3]],), [[1, 10], [5, 3], [9, 0]]),
    (([[1, 2, 1], [1, 2, 2], [1, 2, 3]],), [[1, 3], [2, 0]]),
    (([[0, 2, 3], [5, 7, 3]],), [[0, 3], [2, 0], [5, 3], [7, 0]]),
    (([[1, 5, 3]],), [[1, 3], [5, 0]]),
    (([],), []),
]


def solve(buildings: list[list[int]]) -> list[list[int]]:
    return get_skyline(buildings)


def check() -> None:
    for args, expected in CASES:
        assert get_skyline(*args) == expected
        assert get_skyline_divide(*args) == expected  # both solutions agree
