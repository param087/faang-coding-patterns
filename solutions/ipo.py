"""IPO — LeetCode 502."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "insight": "Capital never shrinks, so what becomes affordable stays affordable — sort by capital, unlock as you go, take the fattest profit in reach.",
    "time": "O(n log n + k log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
You start with capital `w` and may run at most `k` projects. Project i needs
`capital[i]` on hand and returns `profits[i]` **on top of** what you already
have. Maximise the final capital.

The clarification that unlocks everything: **profit is added, never spent**.
Capital is monotonically non-decreasing, so the affordable set only ever grows.
If profits could be negative — or if capital were consumed — this greedy is
dead and you are in knapsack territory. Ask, then say why it matters.

Also confirm projects are one-shot (each runnable at most once) and that
finishing fewer than k projects is allowed.
""",
        ),
        (
            "The insight",
            """
Two wrong first answers, both worth naming before you write the right one:

1. **Sort by profit descending, take the first k you can afford.** Fails on
   `k = 2, w = 0, profits = [1, 100], capital = [0, 1]`: the greedy skips the
   1-profit project because 100 looks better, cannot afford 100, and finishes
   with 0 instead of 101. Cheap projects are how you buy expensive ones.
2. **Rescan the whole array each round for the best affordable project.** It is
   correct, but O(k·n) — at k = n = 10⁵ that is 10¹⁰ operations.

The right frame: the choice is always "the most profitable project among those
I can currently afford", and the affordable set only grows. So

- **sort projects by capital ascending** and keep one pointer into that order;
- before each pick, advance the pointer, pushing every newly affordable
  project's profit into a **max-heap**;
- pop the heap once. That project is the best available move, and taking it can
  only unlock more.

Each project is sorted once and enters the heap at most once, so the total work
is O(n log n) for the sort plus O(n log n) for the heap traffic — not O(k·n).
""",
        ),
        (
            "Edge cases and the exchange-argument sketch",
            """
- **Nothing affordable.** With `w = 0` and every `capital[i] > 0` the heap is
  empty on the first round, so `break` — returning `w` unchanged. Without that
  guard you pop an empty heap and crash on the very first LeetCode test.
- **k larger than n** is legal: the loop simply exhausts the projects and
  breaks. Do not assume `k ≤ n`.
- **k = 0** returns `w` immediately.
- **Duplicate capital requirements** are fine — the `while` advances past all
  of them in one go, which is why it is a `while` and not an `if`.
- **Why greedy is safe:** any optimal schedule that does not start with the
  most profitable affordable project can be rewritten to do so. Swap that
  project in first; the schedule stays feasible because capital only rose, and
  the total is unchanged or better. Standard exchange argument — one sentence
  of it is enough to satisfy the "prove it" follow-up.
- **The real follow-up** is "what if profit is a *return rate* on invested
  capital, or projects have deadlines?" — both break monotonicity and push you
  to DP or scheduling, and saying so shows you know why this one was easy.
""",
        ),
    ],
}


def find_maximized_capital(k: int, w: int, profits: list[int], capital: list[int]) -> int:
    projects = sorted(zip(capital, profits, strict=True))  # by capital ascending
    affordable: list[int] = []  # profits, negated for a max-heap
    next_project = 0

    for _ in range(k):
        # Everything now affordable joins the pool; the pool never shrinks.
        while next_project < len(projects) and projects[next_project][0] <= w:
            heapq.heappush(affordable, -projects[next_project][1])
            next_project += 1

        if not affordable:  # capital too low, and it can no longer grow
            break
        w -= heapq.heappop(affordable)  # negated, so subtracting adds

    return w


CASES = [
    ((2, 0, [1, 2, 3], [0, 1, 1]), 4),
    ((3, 0, [1, 2, 3], [0, 1, 2]), 6),
    ((2, 0, [1, 100], [0, 1]), 101),  # kills "sort by profit and take the top k"
    ((1, 0, [1, 2, 3], [1, 1, 2]), 0),  # nothing affordable — the empty-heap break
    ((10, 0, [1, 2, 3], [0, 1, 1]), 6),  # k > n
    ((0, 5, [1, 2], [0, 0]), 5),
    ((2, 1, [5, 1, 3], [2, 0, 4]), 7),
    ((3, 0, [], []), 0),
]


def solve(k: int, w: int, profits: list[int], capital: list[int]) -> int:
    return find_maximized_capital(k, w, list(profits), list(capital))
