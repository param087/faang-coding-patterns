"""Maximum Points You Can Obtain from Cards — LeetCode 1423."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "The cards you take are the awkward part; the n - k you leave behind form one contiguous window, so minimise that instead.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
You take exactly `k` cards, one at a time, from either end of the row.
Maximise the total points on the cards you took.

Ask: is `k` guaranteed `<= n` (LeetCode says yes, but the `k == n` case still
has to fall out of your code rather than crash it)? Can points be negative
(LeetCode says `1 <= points`, which is why "take all of them" is right when
`k == n` — with negatives that would no longer hold, and the problem changes).
""",
        ),
        (
            "The insight",
            """
The set of cards you take is never an arbitrary subset: it is some prefix of
length `i` plus some suffix of length `k - i`. So the cards you **leave** are
always one contiguous block of width `n - k`.

Flip the objective. Instead of maximising over `k + 1` prefix/suffix splits,
minimise the sum of a **fixed-width window** of size `n - k` and subtract it
from the total. One pass, two pointers implied by the width, O(1) memory.

The wrong first answer is the per-step greedy: "take whichever end is larger".
It dies on `[1, 1000, 1]`-shaped inputs generally, and more sharply on
`[100, 40, 17, 9, 73, 75]` with `k = 3`, where the optimum is one card from the
left and two from the right — a choice no local comparison can see, because
taking the small `100 < ...` end first is what unlocks the pair behind it.

The prefix/suffix enumeration is also correct and also O(n); reach for it if
you find the complement easier to get wrong under pressure. But the complement
version is the one that generalises to "minimum window sum", and interviewers
recognise that reframing.
""",
        ),
        (
            "Edge cases",
            """
- **`k == n`** — the window has width 0, so the minimum left-behind sum is 0
  and the answer is the whole total. The guard `if k >= n: return sum(...)`
  states that explicitly; without it, `card_points[i - 0]` happens to cancel
  and the loop still returns the right thing, but do not rely on an accident
  you have to trace to justify.
- **`k == 0`** — the window is the entire array, the minimum equals the total,
  and the answer is 0. Falls out for free.
- **Single card** — `n = 1, k = 1` hits the `k >= n` branch.
- **Overflow** in Java/C++: `n` up to 10⁵ and points up to 10⁴ gives 10⁹, which
  fits in `int` but only just; the running window sum is safe, a careless
  prefix-sum-of-everything variant is not. Python does not care, but say it.
""",
        ),
    ],
}


def max_score(card_points: list[int], k: int) -> int:
    n = len(card_points)
    if k >= n:
        return sum(card_points)

    leave = n - k  # width of the contiguous block left behind
    window = sum(card_points[:leave])
    smallest_left_behind = window

    for i in range(leave, n):
        window += card_points[i] - card_points[i - leave]
        smallest_left_behind = min(smallest_left_behind, window)

    return sum(card_points) - smallest_left_behind


CASES = [
    (([1, 2, 3, 4, 5, 6, 1], 3), 12),
    (([2, 2, 2], 2), 4),
    (([9, 7, 7, 9, 7, 7, 9], 7), 55),  # k == n, take everything
    (([1, 1000, 1], 1), 1),  # the big card is unreachable
    (([100, 40, 17, 9, 73, 75], 3), 248),  # optimum splits both ends
    (([11, 49, 100, 20, 86, 29, 72], 4), 232),
    (([5, 5], 0), 0),
    (([7], 1), 7),
]


def solve(card_points: list[int], k: int) -> int:
    return max_score(card_points, k)
