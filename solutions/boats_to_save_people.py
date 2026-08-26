"""Boats to Save People — LeetCode 881."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "The heaviest person needs a boat regardless; give them the lightest partner who fits, because nobody else could do better with it.",
    "time": "O(n log n) — the sort dominates",
    "space": "O(1) beyond the sort",
    "sections": [
        (
            "What it asks",
            """
Each boat carries **at most two** people and at most `limit` total weight.
Every person's weight is guaranteed `<= limit`. Minimise the number of boats.

The "at most two" cap is the constraint that makes this tractable — say it
back. Without it this is bin packing, which is NP-hard, and the correct answer
becomes "first-fit-decreasing, and here is why it is within 11/9 of optimal".
Candidates who miss the cap start reaching for DP.
""",
        ),
        (
            "The insight",
            """
Sort, then converge from both ends. The heaviest remaining person `hi` is going
on a boat no matter what; the only decision is whether anyone rides with them.
If the lightest remaining person `lo` fits alongside, take them. Otherwise `hi`
sails alone.

Each iteration retires either one person or two, so it is a single O(n) sweep
after the sort.

Note the asymmetry: `hi` always decrements, `lo` only advances when the pair
fits. That asymmetry *is* the algorithm — the loop is driven by the heavy end.
""",
        ),
        (
            "Why the greedy is provably optimal",
            """
Interviewers push on this one, because the greedy is easy to guess and hard to
defend. The exchange argument:

Take any optimal plan. The heaviest person H is on some boat. If the lightest
person L is not with them, then either H sails alone or with someone else, X.

- If H sails alone and L is on some other boat: L fits with H (we checked), so
  move L onto H's boat. L's old boat now holds one fewer person — never more
  boats, possibly one fewer.
- If H sails with X: swap X and L. Since `L <= X`, the boat still fits, and X
  takes L's old slot, which held someone at least as light. Still valid, same
  count.

Either way an optimal plan can be rewritten to contain our greedy choice
without getting worse. Induct on the rest.

Two sanity checks. `[1,2,3,4,5]` with `limit = 6` gives 3 — pairs (1,5) and
(2,4), then 3 alone, hitting the trivial lower bound ⌈n/2⌉. And `[3,2,2,1]`
with `limit = 3` sorts to `[1,2,2,3]` and gives **3**: the 3 sails alone, then
(1,2) pairs, then the last 2 sails alone. Pairing *adjacent* elements after
sorting — (1,2) and (2,3) — would claim 2 boats and be wrong, because the
second pair weighs 5.

One implementation note: when `lo == hi` the guard evaluates `2 × weight`,
which will usually exceed the limit, so the single remaining person correctly
gets their own boat. The `<=` in `while lo <= hi` is load-bearing; `<` loses a
boat on every odd-sized input.
""",
        ),
    ],
}


def num_rescue_boats(people: list[int], limit: int) -> int:
    people = sorted(people)
    lo, hi = 0, len(people) - 1
    boats = 0

    while lo <= hi:
        if people[lo] + people[hi] <= limit:
            lo += 1  # the lightest rides along
        hi -= 1  # the heaviest always sails
        boats += 1

    return boats


CASES = [
    (([1, 2], 3), 1),
    (([3, 2, 2, 1], 3), 3),
    (([3, 5, 3, 4], 5), 4),  # nobody pairs
    (([1, 2, 3, 4, 5], 6), 3),  # hits the ceil(n/2) lower bound
    (([2, 2, 2, 2, 2], 4), 3),  # odd count, everyone pairable
    (([3, 8, 7, 1, 4], 9), 3),
    (([5], 5), 1),  # weight exactly at the limit
    (([], 5), 0),
]


def solve(people: list[int], limit: int) -> int:
    return num_rescue_boats(people, limit)
