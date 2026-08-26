"""Exam Room — LeetCode 855."""

from __future__ import annotations

from bisect import bisect_left, insort
from itertools import pairwise

META = {
    "pattern": "ordered-set",
    "symbol": "ExamRoom",
    "insight": "Only the gaps between occupied seats matter, so keep those seats sorted and score three kinds of gap: left edge, middle, right edge.",
    "time": "O(m) per seat, O(log m) search plus O(m) shift per leave, m = occupied seats",
    "space": "O(m)",
    "sections": [
        (
            "What it asks",
            """
Seats `0 .. n-1` in a row. `seat()` returns the seat maximising the distance to
the **closest** occupied seat, with ties going to the lowest seat number, and an
empty room answering `0`. `leave(p)` frees an occupied seat.

The clarifying question that shapes the whole solution: **how big is `n`
relative to the number of calls?** `n` goes to 10⁹ but there are at most 10⁴
calls, so you can never materialise the row — at most 10⁴ seats are ever
occupied, and the answer is a function of that sorted set alone.

Also confirm `leave(p)` is only called on an occupied seat (LeetCode guarantees
it) and that "distance" is plain `|i - j|`.
""",
        ),
        (
            "The insight",
            """
A candidate seat is never in the middle of nowhere. With the occupied seats
sorted, the best seat is one of exactly three kinds:

- **The left edge, seat 0.** Its distance is `occupied[0]` — the *whole* gap,
  because there is nobody to its left.
- **The middle of a gap `(a, b)`.** Seat `(a + b) // 2`, distance `(b - a) // 2`
  — *half* the gap, because both sides count.
- **The right edge, seat n-1.** Distance `n - 1 - occupied[-1]`, the whole gap
  again.

So `seat()` is one pass over the sorted occupied list keeping the best score;
`leave()` is a binary search and a delete. At 10⁴ calls, an O(m) scan per seat
is 10⁸ elementary steps in the very worst case and comfortably under it in
practice — say that number out loud rather than reaching for a heap first.
""",
        ),
        (
            "The tie-breaks, which is the whole problem",
            """
Every wrong submission here is a tie-break, not an algorithm:

- **Edge gaps are worth their full length, middle gaps half.** Treat the left
  edge as `occupied[0] // 2` and on `n = 10` with seat 0 taken you answer 4
  instead of 9.
- **Seed the best with seat 0 before the loop, and compare with strict `>`.**
  Ties must fall to the lowest seat number; strict `>` keeps the first
  candidate found, and the candidates are generated left to right. Use `>=` and
  `[0, 9]` on `n = 10` answers 6 instead of 4.
- **`(a + b) // 2` floors**, which is exactly what "lowest seat number on a
  tie" means for an odd gap: between 0 and 5 you sit at 2, not 3.
- **`leave` must delete by index**, `pop(bisect_left(...))`, not `remove` after
  a scan. Same asymptotics on a list, but it is the version that survives being
  swapped for a `SortedList`.

The O(log m) version keeps a max-heap of gaps with lazy deletion, but `leave`
then **merges two gaps into one**, so the heap entries need neighbour links and
a validity check against the live set. That is the follow-up to raise if the
interviewer pushes on 10⁵ calls; it is rarely what they want first.
""",
        ),
    ],
}


class ExamRoom:
    def __init__(self, n: int) -> None:
        self.n = n
        self.occupied: list[int] = []  # sorted seat numbers

    def seat(self) -> int:
        if not self.occupied:
            chosen = 0
        else:
            # Left edge first, so ties resolve to the lowest seat number.
            chosen, best = 0, self.occupied[0]  # a whole gap, not half

            for left, right in pairwise(self.occupied):
                distance = (right - left) // 2  # both sides count, so half
                if distance > best:  # strict: earlier candidate wins ties
                    chosen, best = (left + right) // 2, distance

            trailing = self.n - 1 - self.occupied[-1]  # whole gap again
            if trailing > best:
                chosen, best = self.n - 1, trailing

        insort(self.occupied, chosen)
        return chosen

    def leave(self, p: int) -> None:
        self.occupied.pop(bisect_left(self.occupied, p))


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    room = ExamRoom(10)
    assert room.seat() == 0  # empty room
    assert room.seat() == 9  # right edge is worth its full length
    assert room.seat() == 4  # midpoint of (0, 9), floored — not 5
    assert room.seat() == 2  # (0,4) and (4,9) both score 2; the left one wins
    room.leave(4)
    assert room.seat() == 5  # gap (2,9) reopened and now beats everything

    # A single seat, and re-seating it after it is freed.
    tiny = ExamRoom(1)
    assert tiny.seat() == 0
    tiny.leave(0)
    assert tiny.seat() == 0

    # Filling a small room exhausts it in the expected order.
    small = ExamRoom(5)
    assert [small.seat() for _ in range(5)] == [0, 4, 2, 1, 3]
    assert small.occupied == [0, 1, 2, 3, 4]

    # Freeing the left edge makes seat 0 the best again, at distance 9.
    edges = ExamRoom(10)
    assert edges.seat() == 0
    assert edges.seat() == 9
    edges.leave(0)
    assert edges.seat() == 0
    edges.leave(9)
    assert edges.seat() == 9

    # An odd gap floors to the lower seat: between 0 and 5 that is 2.
    odd = ExamRoom(6)
    odd.occupied = [0, 5]
    assert odd.seat() == 2

    # leave() in the middle of a run must not disturb the rest.
    middle = ExamRoom(20)
    for seat in (0, 19, 9, 14, 4):  # (9,19) scores 5, beating (0,9)'s 4
        assert middle.seat() == seat
    middle.leave(9)
    assert middle.occupied == [0, 4, 14, 19]
    assert middle.seat() == 9  # the merged gap (4, 14) is the widest
